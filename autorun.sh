# Define the metrics to evaluate
METRICS="nDCG@10"

# Find all run files recursively (including subdirectories)
find runs -name '*.txt' -type f | while read -r run_file; do
# Skip .gitkeep files
[[ "$(basename "$run_file")" == ".gitkeep" ]] && continue

run_basename=$(basename "$run_file" .txt)
run_dir=$(dirname "$run_file")

# Check if run is in a subdirectory (e.g., runs/beir/)
if [[ "$run_dir" != "runs" ]]; then
  # Get the subdirectory name (e.g., beir, msmarco-passage)
  subdir=$(basename "$run_dir")
  
  # Parse run filename: run.<benchmark>.<model>.<dataset>.txt
  # Remove 'run.' prefix
  run_parts=${run_basename#run.}
  
  # Split by dots to get benchmark, model, dataset
  IFS='.' read -ra PARTS <<< "$run_parts"
  
  if [[ ${#PARTS[@]} -ge 3 ]]; then
    benchmark="${PARTS[0]}"
    model="${PARTS[1]}"
    # Dataset can have dots, so join remaining parts
    dataset=$(IFS='.'; echo "${PARTS[*]:2}")
    
    # Look for matching qrel file in the same subdirectory
    # Qrel files are named: qrels.<benchmark>.<dataset>.txt
    qrel_file="qrels/${subdir}/qrels.${benchmark}.${dataset}.txt"
    
    if [[ -f "$qrel_file" ]]; then
      echo "Evaluating: $run_file with $qrel_file"
      output_name="${benchmark}.${model}.${dataset}"
      python scripts/evaluate.py \
        --run "$run_file" \
        --qrel "$qrel_file" \
        --metrics "$METRICS" \
        --output_json "results/${output_name}_results.json" || true
    else
      echo "Skipping: $run_file (no matching qrel found at $qrel_file)"
    fi
  else
    echo "Skipping: $run_file (unexpected filename format)"
  fi
else
  # Handle root-level files (legacy format)
  if [[ "$run_basename" == "example_run" ]]; then
    # Handle legacy example files
    qrel_file="qrels/example_qrel.txt"
    if [[ -f "$qrel_file" ]]; then
      echo "Evaluating: $run_file with $qrel_file"
      output_name="example"
      python scripts/evaluate.py \
        --run "$run_file" \
        --qrel "$qrel_file" \
        --metrics "$METRICS" \
        --output_json "results/${output_name}_results.json" || true
    fi
  else
    # Parse run filename: run.<benchmark>.<model>.<dataset>.txt
    # Remove 'run.' prefix
    run_parts=${run_basename#run.}
    
    # Split by dots to get benchmark, model, dataset
    IFS='.' read -ra PARTS <<< "$run_parts"
    
    if [[ ${#PARTS[@]} -ge 3 ]]; then
      benchmark="${PARTS[0]}"
      model="${PARTS[1]}"
      # Dataset can have dots, so join remaining parts
      dataset=$(IFS='.'; echo "${PARTS[*]:2}")
      
      # Look for matching qrel file: qrel.<benchmark>.<dataset>.txt (root level)
      qrel_file="qrels/qrel.${benchmark}.${dataset}.txt"
      
      if [[ -f "$qrel_file" ]]; then
        echo "Evaluating: $run_file with $qrel_file"
        output_name="${benchmark}.${model}.${dataset}"
        python scripts/evaluate.py \
          --run "$run_file" \
          --qrel "$qrel_file" \
          --metrics "$METRICS" \
          --output_json "results/${output_name}_results.json" || true
      else
        echo "Skipping: $run_file (no matching qrel found at $qrel_file)"
      fi
    else
      echo "Skipping: $run_file (unexpected filename format)"
    fi
  fi
fi
done

echo "Evaluation complete."
