"""
🎪 PullRequest class - PR-level orchestration and state management

Handles atomic transactions, trigger processing, and environment orchestration.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from .aws import AWSInterface
from .github import GitHubInterface
from .show import Show, short_sha

# Lazy singletons to avoid import-time failures
_github = None
_aws = None


def get_github() -> GitHubInterface:
    global _github
    if _github is None:
        _github = GitHubInterface()
    return _github


def get_aws() -> AWSInterface:
    global _aws
    if _aws is None:
        _aws = AWSInterface()
    return _aws


# Use get_github() and get_aws() directly in methods


@dataclass
class SyncResult:
    """Result of a PullRequest.sync() operation"""

    success: bool
    action_taken: str  # create_environment, rolling_update, cleanup, no_action
    show: Optional[Show] = None
    error: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result of a PullRequest.analyze() operation"""

    action_needed: str
    build_needed: bool
    sync_needed: bool
    target_sha: str


class PullRequest:
    """GitHub PR with its shows parsed from circus labels"""

    def __init__(self, pr_number: int, labels: List[str]):
        self.pr_number = pr_number
        self.labels = labels
        self._shows = self._parse_shows_from_labels()

    @property
    def shows(self) -> List[Show]:
        """All shows found in labels"""
        return self._shows

    @property
    def current_show(self) -> Optional[Show]:
        """The currently active show (from 🎯 label)"""
        # Find the SHA that's marked as active (🎯)
        active_sha = None
        for label in self.labels:
            if label.startswith("🎪 🎯 "):
                active_sha = label.split(" ")[2]
                break

        if not active_sha:
            return None

        # Find the show with that SHA
        for show in self.shows:
            if show.sha == active_sha:
                return show

        return None

    @property
    def building_show(self) -> Optional[Show]:
        """The currently building show (from 🏗️ label)"""
        building_sha = None
        for label in self.labels:
            if label.startswith("🎪 🏗️ "):
                building_sha = label.split(" ")[2]
                break

        if not building_sha:
            return None

        for show in self.shows:
            if show.sha == building_sha:
                return show

        return None

    @property
    def circus_labels(self) -> List[str]:
        """All circus tent emoji labels"""
        return [label for label in self.labels if label.startswith("🎪")]

    @property
    def has_shows(self) -> bool:
        """Check if PR has any active shows"""
        return len(self.shows) > 0

    def get_show_by_sha(self, sha: str) -> Optional[Show]:
        """Get show by SHA"""
        for show in self.shows:
            if show.sha == sha:
                return show
        return None

    def _parse_shows_from_labels(self) -> List[Show]:
        """Parse all shows from circus tent labels"""
        # Find all unique SHAs from circus labels
        shas = set()
        for label in self.labels:
            if not label.startswith("🎪"):
                continue
            parts = label.split(" ")
            if len(parts) >= 3 and len(parts[1]) == 7:  # SHA is 7 chars
                shas.add(parts[1])

        # Create Show objects for each SHA
        shows = []
        for sha in shas:
            show = Show.from_circus_labels(self.pr_number, self.labels, sha)
            if show:
                shows.append(show)

        return shows

    @classmethod
    def from_id(cls, pr_number: int) -> "PullRequest":
        """Load PR with current labels from GitHub"""
        labels = get_github().get_labels(pr_number)
        return cls(pr_number, labels)

    def refresh_labels(self) -> None:
        """Refresh labels from GitHub and reparse shows"""
        self.labels = get_github().get_labels(self.pr_number)
        self._shows = self._parse_shows_from_labels()

    def analyze(self, target_sha: str, pr_state: str = "open") -> AnalysisResult:
        """Analyze what actions are needed (read-only, for --check-only)

        Args:
            target_sha: Target commit SHA to analyze
            pr_state: PR state (open/closed)

        Returns:
            AnalysisResult with action plan and flags
        """
        # Handle closed PRs
        if pr_state == "closed":
            return AnalysisResult(
                action_needed="cleanup", build_needed=False, sync_needed=True, target_sha=target_sha
            )

        # Determine action needed
        action_needed = self._determine_action(target_sha)

        # Determine if Docker build is needed
        build_needed = action_needed in ["create_environment", "rolling_update", "auto_sync"]

        # Determine if sync execution is needed
        sync_needed = action_needed != "no_action"

        return AnalysisResult(
            action_needed=action_needed,
            build_needed=build_needed,
            sync_needed=sync_needed,
            target_sha=target_sha,
        )

    def sync(
        self,
        target_sha: str,
        dry_run_github: bool = False,
        dry_run_aws: bool = False,
        dry_run_docker: bool = False,
    ) -> SyncResult:
        """Sync PR to desired state with atomic transaction management

        Args:
            target_sha: Target commit SHA to sync to
            github: GitHub interface for label operations
            aws: AWS interface for environment operations
            dry_run_github: Skip GitHub operations if True
            dry_run_aws: Skip AWS operations if True
            dry_run_docker: Skip Docker operations if True

        Returns:
            SyncResult with success status and details

        Raises:
            Exception: On unrecoverable errors (caller should handle)
        """

        # 1. Determine what action is needed
        action_needed = self._determine_action(target_sha)

        # 2. Atomic claim for environment changes (PR-level lock)
        if action_needed in ["create_environment", "rolling_update", "auto_sync"]:
            print(f"🔒 Claiming environment for {action_needed}...")
            if not self._atomic_claim(target_sha, action_needed, dry_run_github):
                print("❌ Claim failed - another job is active")
                return SyncResult(
                    success=False,
                    action_taken="claim_failed",
                    error="Another job is already active",
                )
            print("✅ Environment claimed successfully")

        try:
            # 3. Execute action with error handling
            if action_needed == "create_environment":
                show = self._create_new_show(target_sha)
                print(f"🏗️ Creating environment {show.sha}...")
                self._post_building_comment(show, dry_run_github)

                # Phase 1: Docker build
                print("🐳 Building Docker image...")
                show.build_docker(dry_run_docker)
                show.status = "built"
                print("✅ Docker build completed")
                self._update_show_labels(show, dry_run_github)

                # Phase 2: AWS deployment
                print("☁️ Deploying to AWS ECS...")
                show.deploy_aws(dry_run_aws)
                show.status = "running"
                print(f"✅ Deployment completed - environment running at {show.ip}:8080")
                self._update_show_labels(show, dry_run_github)
                
                # Show AWS console URLs for monitoring
                self._show_service_urls(show)

                self._post_success_comment(show, dry_run_github)
                return SyncResult(success=True, action_taken="create_environment", show=show)

            elif action_needed in ["rolling_update", "auto_sync"]:
                old_show = self.current_show
                if not old_show:
                    return SyncResult(
                        success=False,
                        action_taken="no_current_show",
                        error="No current show for rolling update",
                    )
                new_show = self._create_new_show(target_sha)
                print(f"🔄 Rolling update: {old_show.sha} → {new_show.sha}")
                self._post_rolling_start_comment(old_show, new_show, dry_run_github)

                # Phase 1: Docker build  
                print("🐳 Building updated Docker image...")
                new_show.build_docker(dry_run_docker)
                new_show.status = "built"
                print("✅ Docker build completed")
                self._update_show_labels(new_show, dry_run_github)

                # Phase 2: Blue-green deployment
                print("☁️ Deploying updated environment...")
                new_show.deploy_aws(dry_run_aws)
                new_show.status = "running"
                print(f"✅ Rolling update completed - new environment at {new_show.ip}:8080")
                self._update_show_labels(new_show, dry_run_github)
                
                # Show AWS console URLs for monitoring
                self._show_service_urls(new_show)

                self._post_rolling_success_comment(old_show, new_show, dry_run_github)
                return SyncResult(success=True, action_taken=action_needed, show=new_show)

            elif action_needed == "destroy_environment":
                if self.current_show:
                    print(f"🗑️ Destroying environment {self.current_show.sha}...")
                    self.current_show.stop(dry_run_github=dry_run_github, dry_run_aws=dry_run_aws)
                    print("☁️ AWS resources deleted")
                    self._post_cleanup_comment(self.current_show, dry_run_github)
                    # Remove all circus labels after successful stop
                    if not dry_run_github:
                        get_github().remove_circus_labels(self.pr_number)
                        print("🏷️ GitHub labels cleaned up")
                    print("✅ Environment destroyed")
                return SyncResult(success=True, action_taken="destroy_environment")

            else:
                return SyncResult(success=True, action_taken="no_action")

        except Exception as e:
            # Transaction failed - set failed state and update labels
            if "show" in locals():
                show.status = "failed"
                self._update_show_labels(show, dry_run_github)
                # TODO: Post failure comment
            return SyncResult(success=False, action_taken="failed", error=str(e))

    def start_environment(self, sha: Optional[str] = None, **kwargs: Any) -> SyncResult:
        """Start a new environment (CLI start command logic)"""
        target_sha = sha or get_github().get_latest_commit_sha(self.pr_number)
        return self.sync(target_sha, **kwargs)

    def stop_environment(self, **kwargs: Any) -> SyncResult:
        """Stop current environment (CLI stop command logic)"""
        if not self.current_show:
            return SyncResult(
                success=True, action_taken="no_environment", error="No environment to stop"
            )

        try:
            self.current_show.stop(**kwargs)
            # Remove all circus labels after successful stop
            if not kwargs.get("dry_run_github", False):
                get_github().remove_circus_labels(self.pr_number)
            return SyncResult(success=True, action_taken="stopped")
        except Exception as e:
            return SyncResult(success=False, action_taken="stop_failed", error=str(e))

    def get_status(self) -> dict:
        """Get current status (CLI status command logic)"""
        if not self.current_show:
            return {"status": "no_environment", "show": None}

        return {
            "status": "active",
            "show": {
                "sha": self.current_show.sha,
                "status": self.current_show.status,
                "ip": self.current_show.ip,
                "ttl": self.current_show.ttl,
                "requested_by": self.current_show.requested_by,
                "created_at": self.current_show.created_at,
                "aws_service_name": self.current_show.aws_service_name,
            },
        }

    @classmethod
    def list_all_environments(cls) -> List[dict]:
        """List all environments across all PRs (CLI list command logic)"""
        # Find all PRs with circus tent labels
        pr_numbers = get_github().find_prs_with_shows()

        all_environments = []
        for pr_number in pr_numbers:
            pr = cls.from_id(pr_number)
            # Show ALL environments, not just current_show
            for show in pr.shows:
                # Determine show type based on pointer presence
                show_type = "orphaned"  # Default
                
                # Check for active pointer
                if any(label == f"🎪 🎯 {show.sha}" for label in pr.labels):
                    show_type = "active"
                # Check for building pointer  
                elif any(label == f"🎪 🏗️ {show.sha}" for label in pr.labels):
                    show_type = "building"
                # No pointer = orphaned
                
                environment_data = {
                    "pr_number": pr_number,
                    "status": "active",  # Keep for compatibility
                    "show": {
                        "sha": show.sha,
                        "status": show.status,
                        "ip": show.ip,
                        "ttl": show.ttl,
                        "requested_by": show.requested_by,
                        "created_at": show.created_at,
                        "aws_service_name": show.aws_service_name,
                        "show_type": show_type,  # New field for display
                    },
                }
                all_environments.append(environment_data)

        return all_environments

    def _determine_action(self, target_sha: str) -> str:
        """Determine what sync action is needed based on target SHA state"""
        target_sha_short = target_sha[:7]  # Ensure we're working with short SHA
        
        # Get the specific show for the target SHA
        target_show = self.get_show_by_sha(target_sha_short)
        
        # Check for explicit trigger labels
        trigger_labels = [label for label in self.labels if "showtime-trigger-" in label]

        if trigger_labels:
            for trigger in trigger_labels:
                if "showtime-trigger-start" in trigger:
                    if not target_show or target_show.status == "failed":
                        return "create_environment"  # New SHA or failed SHA
                    elif target_show.status in ["building", "built", "deploying"]:
                        return "no_action"  # Target SHA already in progress
                    elif target_show.status == "running":
                        return "create_environment"  # Force rebuild with trigger
                    else:
                        return "create_environment"  # Default for unknown states
                elif "showtime-trigger-stop" in trigger:
                    return "destroy_environment"

        # No explicit triggers - check target SHA state
        if not target_show:
            # Target SHA doesn't exist - create it
            return "create_environment"
        elif target_show.status == "failed":
            # Target SHA failed - rebuild it
            return "create_environment"
        elif target_show.status in ["building", "built", "deploying"]:
            # Target SHA in progress - wait
            return "no_action"
        elif target_show.status == "running":
            # Target SHA already running - no action needed
            return "no_action"

        return "no_action"

    def _atomic_claim(self, target_sha: str, action: str, dry_run: bool = False) -> bool:
        """Atomically claim this PR for the current job based on target SHA state"""
        target_sha_short = target_sha[:7]
        target_show = self.get_show_by_sha(target_sha_short)
        
        # 1. Validate current state allows this action for target SHA
        if action in ["create_environment", "rolling_update", "auto_sync"]:
            if target_show and target_show.status in [
                "building",
                "built", 
                "deploying",
            ]:
                return False  # Target SHA already in progress
            
            # Allow actions on failed, running, or non-existent target SHAs
            return True

        if dry_run:
            print(f"🎪 [DRY-RUN] Would atomically claim PR for {action}")
            return True

        # 2. Remove trigger labels (atomic operation)
        trigger_labels = [label for label in self.labels if "showtime-trigger-" in label]
        if trigger_labels:
            print(f"🏷️ Removing trigger labels: {trigger_labels}")
            for trigger_label in trigger_labels:
                get_github().remove_label(self.pr_number, trigger_label)
        else:
            print("🏷️ No trigger labels to remove")

        # 3. Set building state immediately (claim the PR)
        if action in ["create_environment", "rolling_update", "auto_sync"]:
            building_show = self._create_new_show(target_sha)
            building_show.status = "building"
            
            # Update labels to reflect building state
            print(f"🏷️ Removing existing circus labels...")
            get_github().remove_circus_labels(self.pr_number)
            
            new_labels = building_show.to_circus_labels()
            print(f"🏷️ Creating new labels: {new_labels}")
            for label in new_labels:
                try:
                    get_github().add_label(self.pr_number, label)
                    print(f"  ✅ Added: {label}")
                except Exception as e:
                    print(f"  ❌ Failed to add {label}: {e}")
                    raise

        return True

    def _create_new_show(self, target_sha: str) -> Show:
        """Create a new Show object for the target SHA"""
        return Show(
            pr_number=self.pr_number,
            sha=short_sha(target_sha),
            status="building",
            created_at=datetime.utcnow().strftime("%Y-%m-%dT%H-%M"),
            ttl="24h",
            requested_by=os.getenv("GITHUB_ACTOR", "unknown"),
        )

    def _post_building_comment(self, show: Show, dry_run: bool = False) -> None:
        """Post building comment for new environment"""
        from .github_messages import building_comment

        if not dry_run:
            comment = building_comment(show)
            get_github().post_comment(self.pr_number, comment)

    def _post_success_comment(self, show: Show, dry_run: bool = False) -> None:
        """Post success comment for completed environment"""
        from .github_messages import success_comment

        if not dry_run:
            comment = success_comment(show)
            get_github().post_comment(self.pr_number, comment)

    def _post_rolling_start_comment(
        self, old_show: Show, new_show: Show, dry_run: bool = False
    ) -> None:
        """Post rolling update start comment"""
        from .github_messages import rolling_start_comment

        if not dry_run:
            full_sha = new_show.sha + "0" * (40 - len(new_show.sha))
            comment = rolling_start_comment(old_show, full_sha)
            get_github().post_comment(self.pr_number, comment)

    def _post_rolling_success_comment(
        self, old_show: Show, new_show: Show, dry_run: bool = False
    ) -> None:
        """Post rolling update success comment"""
        from .github_messages import rolling_success_comment

        if not dry_run:
            comment = rolling_success_comment(old_show, new_show)
            get_github().post_comment(self.pr_number, comment)

    def _post_cleanup_comment(self, show: Show, dry_run: bool = False) -> None:
        """Post cleanup completion comment"""
        from .github_messages import cleanup_comment

        if not dry_run:
            comment = cleanup_comment(show)
            get_github().post_comment(self.pr_number, comment)

    def stop_if_expired(self, max_age_hours: int, dry_run: bool = False) -> bool:
        """Stop environment if it's expired based on age

        Args:
            max_age_hours: Maximum age in hours before expiration
            dry_run: If True, just check don't actually stop

        Returns:
            True if environment was expired (and stopped), False otherwise
        """
        if not self.current_show:
            return False

        # Use Show's expiration logic
        if self.current_show.is_expired(max_age_hours):
            if dry_run:
                print(f"🎪 [DRY-RUN] Would stop expired environment: PR #{self.pr_number}")
                return True

            print(f"🧹 Stopping expired environment: PR #{self.pr_number}")
            result = self.stop_environment(dry_run_github=False, dry_run_aws=False)
            return result.success

        return False  # Not expired

    @classmethod
    def find_all_with_environments(cls) -> List[int]:
        """Find all PR numbers that have active environments"""
        return get_github().find_prs_with_shows()

    def _update_show_labels(self, show: Show, dry_run: bool = False) -> None:
        """Update GitHub labels to reflect show state with proper status replacement"""
        if dry_run:
            return

        # Refresh labels to get current state (atomic claim may have changed them)
        self.refresh_labels()

        # First, remove any existing status labels for this SHA to ensure clean transitions
        sha_status_labels = [
            label for label in self.labels 
            if label.startswith(f"🎪 {show.sha} 🚦 ")
        ]
        for old_status_label in sha_status_labels:
            get_github().remove_label(self.pr_number, old_status_label)

        # Now do normal differential updates - only for this SHA
        current_sha_labels = {
            label for label in self.labels 
            if label.startswith("🎪") and (
                label.startswith(f"🎪 {show.sha} ") or  # SHA-first format: 🎪 abc123f 📅 ...
                label.startswith(f"🎪 🎯 {show.sha}") or  # Pointer format: 🎪 🎯 abc123f
                label.startswith(f"🎪 🏗️ {show.sha}")    # Building pointer: 🎪 🏗️ abc123f
            )
        }
        desired_labels = set(show.to_circus_labels())

        # Remove the status labels we already cleaned up from the differential
        current_sha_labels = current_sha_labels - set(sha_status_labels)

        # Only add labels that don't exist
        labels_to_add = desired_labels - current_sha_labels
        for label in labels_to_add:
            get_github().add_label(self.pr_number, label)

        # Only remove labels that shouldn't exist (excluding status labels already handled)
        labels_to_remove = current_sha_labels - desired_labels
        for label in labels_to_remove:
            get_github().remove_label(self.pr_number, label)

        # Final refresh to update cache with all changes
        self.refresh_labels()

    def _show_service_urls(self, show: Show) -> None:
        """Show AWS console URLs for monitoring deployment"""
        from .github_messages import get_aws_console_urls
        
        urls = get_aws_console_urls(show.ecs_service_name)
        print(f"\n🎪 Monitor deployment progress:")
        print(f"📝 Logs: {urls['logs']}")
        print(f"📊 Service: {urls['service']}")
        print("")
