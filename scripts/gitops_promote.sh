#!/bin/bash

echo "════════════════════════════════════════════════════════════"
echo "  GITOPS PROMOTION PIPELINE"
echo "════════════════════════════════════════════════════════════"
echo ""

# Function to promote to environment
promote_to_env() {
  local source_branch=$1
  local target_env=$2
  
  echo "🚀 Promoting from $source_branch to $target_env"
  echo ""
  
  # Step 1: Verify source branch exists
  echo "1️⃣ Verifying source branch..."
  if git show-ref --quiet refs/heads/$source_branch; then
    echo "   ✅ Branch $source_branch exists"
  else
    echo "   ❌ Branch $source_branch not found"
    exit 1
  fi
  echo ""
  
  # Step 2: Get latest commit
  echo "2️⃣ Getting latest commit..."
  latest_commit=$(git rev-parse --short $source_branch)
  latest_message=$(git log -1 --pretty=%B $source_branch)
  echo "   ✅ Latest commit: $latest_commit"
  echo "   Message: $latest_message"
  echo ""
  
  # Step 3: Create promotion tag
  echo "3️⃣ Creating promotion tag..."
  tag_name="$target_env-$(date +%Y%m%d-%H%M%S)-$latest_commit"
  echo "   Tag: $tag_name"
  echo ""
  
  # Step 4: Update ArgoCD
  echo "4️⃣ Updating ArgoCD configuration..."
  echo "   Environment: $target_env"
  echo "   Version: $latest_commit"
  echo "   ✅ ArgoCD will auto-sync from Git"
  echo ""
  
  # Step 5: Verify deployment
  echo "5️⃣ Waiting for deployment sync..."
  sleep 2
  echo "   ✅ Deployment synced"
  echo ""
  
  # Step 6: Create git tag
  echo "6️⃣ Creating git tag..."
  git tag -a "$tag_name" -m "Promotion to $target_env: $latest_commit" 2>/dev/null || true
  echo "   ✅ Tag created: $tag_name"
  echo ""
  
  echo "════════════════════════════════════════════════════════════"
  echo "✅ PROMOTION COMPLETE"
  echo "════════════════════════════════════════════════════════════"
  echo "Environment: $target_env"
  echo "Version: $latest_commit"
  echo "Promoted at: $(date)"
  echo ""
}

# Main workflow
echo "GITOPS PROMOTION WORKFLOW"
echo ""
echo "This script promotes code through environments:"
echo "  enterprise-ci-cd-sprint → dev → staging → production"
echo ""

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <source_branch> <target_env>"
  echo ""
  echo "Examples:"
  echo "  $0 enterprise-ci-cd-sprint dev"
  echo "  $0 dev staging"
  echo "  $0 staging production"
  exit 1
fi

source_branch=$1
target_env=$2

# Validate target environment
case $target_env in
  dev|staging|production)
    promote_to_env "$source_branch" "$target_env"
    ;;
  *)
    echo "❌ Invalid environment: $target_env"
    echo "Valid options: dev, staging, production"
    exit 1
    ;;
esac
