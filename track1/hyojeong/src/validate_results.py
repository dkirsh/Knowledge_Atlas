import os
import json

def load_json(filepath):
    """Helper function to read JSON files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    base_dir = os.path.dirname(__file__)
    results_path = os.path.join(base_dir, "../data/search_results.json")
    
    # 1. Check if the output file exists
    if not os.path.exists(results_path):
        print("❌ Validation Failed: search_results.json does not exist.")
        return
        
    try:
        records = load_json(results_path)
    except json.JSONDecodeError as e:
        print(f"❌ Validation Failed: search_results.json is not a valid JSON file. Error: {e}")
        return

    total_count = len(records)
    print("📋 Starting Data Validation Pipeline...")
    print(f"Total records found: {total_count}")

    # 2. Check minimum count requirement (Must be >= 500)
    MIN_REQUIRED = 500
    if total_count >= MIN_REQUIRED:
        print(f"  ✅ Requirement Check: Total images ({total_count}) meets the minimum requirement of {MIN_REQUIRED}.")
    else:
        print(f"  ❌ Requirement Check Failed: Total images ({total_count}) is less than {MIN_REQUIRED}.")

    # 3. Check for structural integrity and missing essential fields
    required_fields = ["url", "thumbnail_url", "source_name", "source_page_url", "license", "space_type"]
    missing_field_counts = {field: 0 for field in required_fields}
    corrupted_records = 0

    for record in records:
        is_corrupted = False
        for field in required_fields:
            # Check if field is missing or empty/null
            if field not in record or not record[field]:
                missing_field_counts[field] += 1
                is_corrupted = True
        if is_corrupted:
            corrupted_records += 1

    print("\n🔍 Structural Integrity Report:")
    has_errors = False
    for field, count in missing_field_counts.items():
        if count > 0:
            print(f"  ⚠️ Field '{field}' is missing or null in {count} records.")
            has_errors = True
        else:
            print(f"  ✅ Field '{field}': 0 missing values.")

    # 4. Final Verdict
    print("\n==========================================")
    if total_count >= MIN_REQUIRED and not has_errors:
        print("🎉 FINAL VERDICT: VALIDATION SUCCESS!")
        print("The dataset complies with all contract specifications.")
    else:
        print("❌ FINAL VERDICT: VALIDATION FAILED")
        print(f"Please review the {corrupted_records} corrupted records noted above.")
    print("==========================================")

if __name__ == "__main__":
    main()