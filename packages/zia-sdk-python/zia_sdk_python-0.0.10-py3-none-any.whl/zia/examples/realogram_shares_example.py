#!/usr/bin/env python3
"""
Example demonstrating how to work with realogram and share of shelf data.

This example shows how to:
1. Parse realogram data from modalities in annotations
2. Parse share of shelf data from postprocessing results
3. Extract and analyze all modalities (is-beer, orientation, realogram)
4. Extract and analyze share of shelf values
"""

import json
from pathlib import Path

from zia.models.image_recognition import (
    NLIRResult,
    NLIRModalities,
    NLIRShare,
    NLIRPostprocessingResults,
)


def load_sample_data():
    """Load sample data from the JSON file."""
    sample_file = Path(__file__).parent.parent.parent / "data" / "display" / "sample_ab_realogram_sos.json"
    
    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return None
    
    with open(sample_file, 'r') as f:
        return json.load(f)


def analyze_modalities_data(result: NLIRResult):
    """Analyze all modalities data from annotations."""
    if not result.coco or result.status.value != "PROCESSED":
        print("No COCO data available or result not processed")
        return
    
    modality_annotations = []
    
    for annotation in result.coco.annotations:
        if not annotation.neurolabs or not annotation.neurolabs.modalities:
            continue
        
        modalities = annotation.neurolabs.modalities
        modality_data = {
            "annotation_id": annotation.id,
            "detection_score": annotation.neurolabs.score,
        }
        
        # Extract is-beer modality
        if modalities.is_beer and modalities.is_beer:
            modality_data["is_beer"] = modalities.is_beer[0].value
            modality_data["is_beer_score"] = modalities.is_beer[0].score
        
        # Extract orientation modality
        if modalities.orientation and modalities.orientation:
            modality_data["orientation"] = modalities.orientation[0].value
            modality_data["orientation_score"] = modalities.orientation[0].score
        
        # Extract realogram modalities
        if modalities.realogram_slot and modalities.realogram_slot:
            modality_data["slot"] = modalities.realogram_slot[0].value
            modality_data["slot_score"] = modalities.realogram_slot[0].score
        
        if modalities.realogram_shelf and modalities.realogram_shelf:
            modality_data["shelf"] = modalities.realogram_shelf[0].value
            modality_data["shelf_score"] = modalities.realogram_shelf[0].score
        
        if modalities.realogram_stack and modalities.realogram_stack:
            modality_data["stack"] = modalities.realogram_stack[0].value
            modality_data["stack_score"] = modalities.realogram_stack[0].score
        
        if len(modality_data) > 2:  # More than just annotation_id and detection_score
            modality_annotations.append(modality_data)
    
    if not modality_annotations:
        print("No modality data found in annotations")
        return
    
    print(f"\n=== Modalities Analysis ===")
    print(f"Total annotations with modalities: {len(modality_annotations)}")
    
    # Analyze is-beer distribution
    is_beer_data = [a for a in modality_annotations if "is_beer" in a]
    if is_beer_data:
        is_beer_values = [a["is_beer"] for a in is_beer_data]
        print(f"\nIs-beer distribution:")
        for value in set(is_beer_values):
            count = is_beer_values.count(value)
            print(f"  {value}: {count} annotations")
    
    # Analyze orientation distribution
    orientation_data = [a for a in modality_annotations if "orientation" in a]
    if orientation_data:
        orientation_values = [a["orientation"] for a in orientation_data]
        print(f"\nOrientation distribution:")
        for value in set(orientation_values):
            count = orientation_values.count(value)
            print(f"  {value}: {count} annotations")
    
    # Analyze realogram data
    realogram_data = [a for a in modality_annotations if "shelf" in a]
    if realogram_data:
        print(f"\nRealogram data:")
        
        # Group by shelf
        shelf_groups = {}
        for annotation in realogram_data:
            shelf = annotation.get("shelf")
            if shelf not in shelf_groups:
                shelf_groups[shelf] = []
            shelf_groups[shelf].append(annotation)
        
        print(f"Shelf distribution:")
        for shelf, annotations in sorted(shelf_groups.items()):
            print(f"  Shelf {shelf}: {len(annotations)} annotations")
            
            # Show slot distribution for this shelf
            slots = {}
            for annotation in annotations:
                slot = annotation.get("slot")
                if slot not in slots:
                    slots[slot] = []
                slots[slot].append(annotation)
            
            for slot, slot_annotations in sorted(slots.items()):
                print(f"    Slot {slot}: {len(slot_annotations)} annotations")
                for annotation in slot_annotations:
                    stack = annotation.get("stack", "N/A")
                    score = annotation.get("detection_score", 0)
                    orientation = annotation.get("orientation", "N/A")
                    is_beer = annotation.get("is_beer", "N/A")
                    print(f"      - Annotation {annotation['annotation_id']} (stack {stack}, score {score:.3f}, orientation {orientation}, is-beer {is_beer})")


def analyze_share_of_shelf_data(result: NLIRResult):
    """Analyze share of shelf data from postprocessing results."""
    if not result.postprocessing_results or not result.postprocessing_results.shares:
        print("No share of shelf data available")
        return
    
    shares = result.postprocessing_results.shares
    
    print(f"\n=== Share of Shelf Analysis ===")
    print(f"Total share entries: {len(shares)}")
    
    for share in shares:
        print(f"\nImage {share.image_id}:")
        print(f"  Total values: {len(share.values)}")
        
        # Group by group_by criteria
        group_by_categories = {}
        for value in share.values:
            group_by = value.group_by
            if group_by not in group_by_categories:
                group_by_categories[group_by] = []
            group_by_categories[group_by].append(value)
        
        for group_by, values in group_by_categories.items():
            print(f"  {group_by.title()}:")
            
            # Sort by count ratio (descending)
            sorted_values = sorted(values, key=lambda x: x.count_ratio, reverse=True)
            
            for value in sorted_values[:5]:  # Show top 5
                product_info = f"Product {value.product_uuid[:8]}..." if value.product_uuid else "Unknown"
                print(f"    {product_info}:")
                print(f"      Count: {value.count} ({value.count_ratio:.1%})")
                print(f"      Area: {value.area} pixels ({value.area_ratio:.1%})")


def main():
    """Main example function."""
    print("Modalities and Share of Shelf Analysis Example")
    print("=" * 50)
    
    # Load sample data
    sample_data = load_sample_data()
    if not sample_data:
        return
    
    # Parse the result
    try:
        result = NLIRResult.model_validate(sample_data)
        print(f"Successfully parsed result: {result.uuid}")
        print(f"Status: {result.status.value}")
        print(f"Duration: {result.duration:.2f} seconds")
    except Exception as e:
        print(f"Error parsing result: {e}")
        return
    
    # Analyze modalities data from annotations
    analyze_modalities_data(result)
    
    # Analyze share of shelf data
    analyze_share_of_shelf_data(result)
    
    # Show how to access specific data
    print(f"\n=== Direct Data Access Examples ===")
    
    # Access modalities data directly
    if result.coco and result.coco.annotations:
        modality_annotations = []
        for annotation in result.coco.annotations:
            if (annotation.neurolabs and annotation.neurolabs.modalities):
                modality_annotations.append(annotation)
        
        if modality_annotations:
            first_annotation = modality_annotations[0]
            modalities = first_annotation.neurolabs.modalities
            
            # Access different modality types
            if modalities.is_beer and modalities.is_beer:
                is_beer = modalities.is_beer[0].value
                is_beer_score = modalities.is_beer[0].score
                print(f"First annotation is-beer: {is_beer} (score: {is_beer_score})")
            
            if modalities.orientation and modalities.orientation:
                orientation = modalities.orientation[0].value
                orientation_score = modalities.orientation[0].score
                print(f"First annotation orientation: {orientation} (score: {orientation_score})")
            
            if modalities.realogram_slot and modalities.realogram_slot:
                slot = modalities.realogram_slot[0].value
                slot_score = modalities.realogram_slot[0].score
                print(f"First annotation slot: {slot} (score: {slot_score})")
    
    # Access share data
    if result.postprocessing_results and result.postprocessing_results.shares:
        shares = result.postprocessing_results.shares
        if shares and shares[0].values:
            first_share = shares[0].values[0]
            print(f"First share value: {first_share.group_by} - {first_share.count} items ({first_share.count_ratio:.1%})")


if __name__ == "__main__":
    main()
