import subprocess
import sys


def check_git_updates(logger):
    logger.info("Checking for git repository updates...")
    try:
        # 1. Check if it's a git repo
        is_repo = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
        if is_repo.returncode != 0:
            logger.warning(
                "Not a git repository. Please consider to use git for tracking updates."
            )
            return

        # 2. Fetch remote changes
        subprocess.run(["git", "fetch"], capture_output=True)

        # 3. Get the hashes for LOCAL, REMOTE and BASE
        def get_hash(command):
            return subprocess.check_output(command).decode("utf-8").strip()

        # Get current branch name (e.g., 'main' or 'master')
        branch = get_hash(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        # Reference to the upstream (tracking) branch
        upstream = f"@{'{u}'}"  # Simplified git notation for 'upstream'

        local_hash = get_hash(["git", "rev-parse", "HEAD"])
        remote_hash = get_hash(["git", "rev-parse", upstream])
        base_hash = get_hash(["git", "merge-base", "HEAD", upstream])

        # 4. Compare hashes
        if local_hash == remote_hash:
            # Everything is up to date
            return
        elif local_hash == base_hash:
            logger.error(f"Newer commits found on remote for branch '{branch}'.")
            logger.warning("Please run 'git pull' before executing the program.")
            sys.exit(1)
        elif remote_hash == base_hash:
            logger.warning(
                "Local repository is ahead of remote. Consider pushing changes."
            )
            # You have local commits not pushed yet, but that's fine
            return
        else:
            # Branches have diverged
            logger.error("Local and remote branches have diverged.")
            sys.exit(1)

    except subprocess.CalledProcessError:
        logger.warning("No git upstream set, failing to check repository updates.")
        pass
    except FileNotFoundError:
        logger.warning("Failed to run git command for checking repository updates.")
        pass
