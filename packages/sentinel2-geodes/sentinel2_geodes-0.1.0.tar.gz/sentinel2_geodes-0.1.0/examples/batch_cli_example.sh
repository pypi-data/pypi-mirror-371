#!/bin/bash

# Batch Processing Example using CLI
# This example shows how to process multiple agricultural fields in batch mode

echo "========================================"
echo "Batch Processing with CLI"
echo "========================================"

# 1. Create multiple GeoJSON files with different dates
echo "Creating sample GeoJSON files..."

# Field 1: Summer wheat monitoring
cat > field1_wheat.geojson << 'EOF'
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {
      "Name": "WheatField_North",
      "begin": "2024-06-01T00:00:00Z",
      "end": "2024-08-31T00:00:00Z",
      "crop": "wheat"
    },
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [1.7724, 47.9666],
        [1.7751, 47.9675],
        [1.7777, 47.9643],
        [1.7750, 47.9633],
        [1.7724, 47.9666]
      ]]
    }
  }]
}
EOF

# Field 2: Spring corn monitoring
cat > field2_corn.geojson << 'EOF'
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {
      "Name": "CornField_South",
      "begin": "2024-03-01T00:00:00Z",
      "end": "2024-05-31T00:00:00Z",
      "crop": "corn"
    },
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [1.7800, 47.9600],
        [1.7850, 47.9610],
        [1.7860, 47.9580],
        [1.7810, 47.9570],
        [1.7800, 47.9600]
      ]]
    }
  }]
}
EOF

# Field 3: Vineyard annual monitoring
cat > field3_vineyard.geojson << 'EOF'
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {
      "Name": "VineyardWest",
      "begin": "2024-01-01T00:00:00Z",
      "end": "2024-12-31T00:00:00Z",
      "crop": "vineyard"
    },
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [1.7900, 47.9550],
        [1.7920, 47.9560],
        [1.7940, 47.9540],
        [1.7920, 47.9530],
        [1.7900, 47.9550]
      ]]
    }
  }]
}
EOF

echo "Created 3 GeoJSON files with different date ranges"

# 2. Run batch processing
echo ""
echo "Running batch processing for all fields..."
echo "Each field will use its own dates from GeoJSON properties"
echo ""

sentinel2-geodes batch \
    field1_wheat.geojson \
    field2_corn.geojson \
    field3_vineyard.geojson \
    ./batch_output \
    --cloud 30 \
    --indices NDVI EVI NDWI \
    --csv batch_results.csv

echo ""
echo "========================================"
echo "Batch processing complete!"
echo "========================================"
echo ""
echo "Output structure:"
echo "batch_output/"
echo "├── downloads/        # ZIP files for all areas"
echo "├── crops/           # Cropped bands for all areas"
echo "├── indices/         # NDVI, EVI, NDWI for all areas"
echo "└── batch_results.csv # Combined results for all fields"
echo ""
echo "Each field was processed with its own date range:"
echo "- WheatField_North: June-August 2024 (summer growing season)"
echo "- CornField_South: March-May 2024 (spring planting season)"
echo "- VineyardWest: Full year 2024 (annual monitoring)"