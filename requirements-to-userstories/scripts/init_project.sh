#!/usr/bin/env bash
# Run from the parent directory where you want the project created:
#   bash init_project.sh

set -e
ROOT="requirements-to-userstories"

mkdir -p \
  $ROOT/orchestrator \
  $ROOT/agents/{ingestion,rag_index,sr_analyst,sr_reviewer,feature_derivation,feature_reviewer,story_writer,backlog_reviewer,gate_review} \
  $ROOT/adapters/{doors_ng,jira,confluence,github,vector_db,pdf} \
  $ROOT/rag/{namespaces,embeddings,chunkers} \
  $ROOT/rubrics/{iso26262,aspice,aiag_vda,custom} \
  $ROOT/templates/{stories,specs,reports} \
  $ROOT/config/{profiles,adapters} \
  $ROOT/pipeline/{stages,routing,hitl} \
  $ROOT/tools/{parsers,validators,scorers} \
  $ROOT/docs/{architecture,api,runbooks} \
  $ROOT/tests/{unit,integration,fixtures} \
  $ROOT/scripts

find $ROOT -type d | sort
echo "✓ Project structure created at ./$ROOT"
