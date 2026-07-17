import pandas as pd
import json
import math
import os

def clean_summary(text):
    if pd.isna(text):
        return ""
    text_str = str(text).strip()
    if not text_str:
        return ""
    # Ensure description starts with a capital letter
    return text_str[0].upper() + text_str[1:] if len(text_str) > 0 else text_str

def main():
    file_path = 'assets/data/publications_list.xlsx'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    df = pd.read_excel(file_path)
    
    # Strip column names of whitespace just in case
    df.columns = df.columns.str.strip()
    
    print("Found columns:", df.columns.tolist())
    
    # Dynamic column mapping
    group_col = next((col for col in df.columns if col.lower() in ['type', 'group', 'category']), None)
    citation_col = next((col for col in df.columns if 'citation' in col.lower() or 'apa' in col.lower()), None)
    summary_col = next((col for col in df.columns if 'summary' in col.lower() or 'description' in col.lower()), None)
    link_col = next((col for col in df.columns if 'link' in col.lower() or 'doi' in col.lower()), None)
    date_col = next((col for col in df.columns if 'date' in col.lower() or 'year' in col.lower()), None)
    
    if not all([group_col, citation_col, summary_col, link_col]):
        print("\nWarning: Could not automatically detect all columns based on expected names (Type, Citation, Summary, Link, Date).")
        print("Using positional fallback mapping.")
        cols = df.columns.tolist()
        group_col = cols[0] if len(cols) > 0 else None
        citation_col = cols[1] if len(cols) > 1 else None
        summary_col = cols[2] if len(cols) > 2 else None
        link_col = cols[3] if len(cols) > 3 else None
        date_col = cols[4] if len(cols) > 4 else None

    if date_col:
        df = df.sort_values(by=date_col, ascending=False)
        
    publications = {
        "Working papers": [],
        "Reports and research briefs": [],
        "Academic publications": [],
        "Interviews, videos and other texts": []
    }
    
    for index, row in df.iterrows():
        if group_col and not pd.isna(row[group_col]):
            group = str(row[group_col]).strip()
        else:
            group = "Other"
            
        citation = str(row[citation_col]).strip() if citation_col and not pd.isna(row[citation_col]) else ""
        summary = clean_summary(row[summary_col]) if summary_col else ""
        link = str(row[link_col]).strip() if link_col and not pd.isna(row[link_col]) else ""
        date_val = str(row[date_col]).strip() if date_col and not pd.isna(row[date_col]) else ""
        
        target_group = None
        for g in publications.keys():
            if g.lower() == group.lower() or group.lower() in g.lower():
                target_group = g
                break
        
        if not target_group:
            target_group = "Academic publications"
            
        publications[target_group].append({
            "citation": citation,
            "summary": summary,
            "link": link,
            "date": date_val
        })
        
    out_path = 'assets/data/publications.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(publications, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully processed {len(df)} publications into {out_path}!")
    for g, items in publications.items():
        print(f"  - {g}: {len(items)} items")

if __name__ == "__main__":
    main()
