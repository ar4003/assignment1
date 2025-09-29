import csv

def auto_approve(input_csv='data/phase2_categorized_data.csv', output_csv='data/phase2_approved.csv', min_confidence='Medium'):
    confidence_order = {'Low': 0, 'Medium': 1, 'High': 2}
    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            conf = row.get('ai_confidence', 'Low').capitalize()
            cat = row.get('category', '')
            # Approve if confidence >= threshold and category is relevant
            if confidence_order.get(conf, 0) >= confidence_order.get(min_confidence, 1) and cat != 'Not Relevant':
                row['status'] = 'Run GPT'
            writer.writerow(row)

    print(f"✅ Auto-approved entries written to {output_csv}")

if __name__ == '__main__':
    auto_approve()
