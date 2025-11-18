"""
PDF Quote Generation with Route Map Visualization
Downloads and embeds the route map image in the PDF!
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from typing import Dict
import config
import requests
from io import BytesIO
from pathlib import Path


def download_map_image(map_url: str) -> BytesIO:
    """Download map image from URL and return as BytesIO"""
    try:
        response = requests.get(map_url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            print(f"⚠️  Failed to download map: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️  Error downloading map: {e}")
        return None


def generate_quote_pdf(quote_data: Dict, shipment_data: Dict, output_path: str) -> str:
    """
    Generate a professional freight quote PDF with route map visualization.
    
    Args:
        quote_data: Quote information from API (includes route_map_url)
        shipment_data: Extracted shipment details
        output_path: Path where PDF should be saved
        
    Returns:
        Path to generated PDF file
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # Company Header
    story.append(Paragraph(config.COMPANY_NAME, title_style))
    story.append(Paragraph(f"{config.COMPANY_ADDRESS} | {config.COMPANY_PHONE}", styles['Normal']))
    story.append(Paragraph(f"{config.COMPANY_EMAIL}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Quote Information
    story.append(Paragraph("FREIGHT SHIPPING QUOTE", title_style))
    
    info_data = [
        ["Quote ID:", quote_data['quote_id']],
        ["Quote Date:", datetime.now().strftime("%B %d, %Y")],
        ["Valid Until:", datetime.fromisoformat(quote_data['valid_until'].replace('Z', '')).strftime("%B %d, %Y")],
        ["Transit Time:", f"{quote_data['transit_days']} business days"],
    ]
    
    # Add distance and duration if available
    if 'distance_miles' in quote_data:
        info_data.append(["Distance:", f"{quote_data['distance_miles']:.1f} miles"])
    if 'duration_hours' in quote_data:
        hours = int(quote_data['duration_hours'])
        minutes = int((quote_data['duration_hours'] - hours) * 60)
        info_data.append(["Drive Time:", f"{hours}h {minutes}m"])
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # ROUTE MAP VISUALIZATION
    if quote_data.get('route_map_url'):
        story.append(Paragraph("Route Map", heading_style))
        
        map_image_data = download_map_image(quote_data['route_map_url'])
        
        if map_image_data:
            try:
                # Add map image to PDF
                map_img = Image(map_image_data, width=5*inch, height=3.33*inch)
                story.append(map_img)
                story.append(Spacer(1, 0.2*inch))
                
                # Add map legend
                origin = shipment_data.get('origin', {})
                destination = shipment_data.get('destination', {})
                legend_text = f"""
                <para fontSize=9 textColor="#666666">
                🟢 A: {origin.get('city', 'N/A')}, {origin.get('state', 'N/A')} → 
                🔴 B: {destination.get('city', 'N/A')}, {destination.get('state', 'N/A')}
                </para>
                """
                story.append(Paragraph(legend_text, styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
                
                print(f"✅ Route map embedded in PDF")
            except Exception as e:
                print(f"⚠️  Failed to embed map image: {e}")
        else:
            print("⚠️  Map image not available")
    
    # Shipment Details
    story.append(Paragraph("Shipment Details", heading_style))
    
    origin = shipment_data.get('origin', {})
    destination = shipment_data.get('destination', {})
    cargo = shipment_data.get('cargo', {})
    
    shipment_data_table = [
        ["Origin:", f"{origin.get('city', 'N/A')}, {origin.get('state', 'N/A')} {origin.get('zip', 'N/A')}"],
        ["Destination:", f"{destination.get('city', 'N/A')}, {destination.get('state', 'N/A')} {destination.get('zip', 'N/A')}"],
        ["Commodity:", cargo.get('commodity', 'General Freight')],
        ["Weight:", f"{cargo.get('weight_lbs', 0)} lbs"],
        ["Pieces:", f"{cargo.get('pieces', 0)} {cargo.get('piece_type', 'pieces')}"],
        ["Equipment:", quote_data['equipment_type'].replace('_', ' ').title()],
    ]
    
    # Add dimensions if available
    dims = cargo.get('dimensions', {})
    if dims:
        dim_str = f"{dims.get('length', 0)}\" x {dims.get('width', 0)}\" x {dims.get('height', 0)}\""
        shipment_data_table.append(["Dimensions:", dim_str])
    
    # Add special services
    special = shipment_data.get('special_services', [])
    if special:
        shipment_data_table.append(["Special Services:", ", ".join([s.replace('_', ' ').title() for s in special])])
    
    shipment_table = Table(shipment_data_table, colWidths=[2*inch, 4*inch])
    shipment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(shipment_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Cost Breakdown
    story.append(Paragraph("Cost Breakdown", heading_style))
    
    breakdown = quote_data['breakdown']
    cost_data = [
        ["Item", "Amount"],
        ["Base Rate", f"${breakdown['base_rate']:.2f}"],
        ["Fuel Surcharge", f"${breakdown['fuel_surcharge']:.2f}"],
    ]
    
    if breakdown['liftgate_fee'] > 0:
        cost_data.append(["Liftgate Service", f"${breakdown['liftgate_fee']:.2f}"])
    
    if breakdown.get('climate_control_fee', 0) > 0:
        cost_data.append(["Climate Control", f"${breakdown['climate_control_fee']:.2f}"])
    
    cost_data.append(["Insurance", f"${breakdown['insurance']:.2f}"])
    cost_data.append(["", ""])  # Separator
    cost_data.append(["TOTAL", f"${quote_data['total_cost']:.2f}"])
    
    cost_table = Table(cost_data, colWidths=[4*inch, 2*inch])
    cost_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 10),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1a5490')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
    ]))
    story.append(cost_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Terms and Conditions
    story.append(Paragraph("Terms and Conditions", heading_style))
    terms_text = f"""
    <para fontSize=9>
    • {quote_data['terms']}<br/>
    • This quote is valid until {datetime.fromisoformat(quote_data['valid_until'].replace('Z', '')).strftime('%B %d, %Y')}<br/>
    • Prices are subject to change based on actual pickup date and fuel costs<br/>
    • Additional fees may apply for accessorial services not listed<br/>
    • Shipment must be properly packaged and labeled<br/>
    • Insurance coverage is based on declared value<br/>
    • Transit times are estimates and not guaranteed<br/>
    • Distance and time calculated using real-time route data<br/>
    </para>
    """
    story.append(Paragraph(terms_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    story.append(Paragraph("Questions? Contact Us:", heading_style))
    contact_text = f"""
    <para fontSize=10>
    <b>Phone:</b> {config.COMPANY_PHONE}<br/>
    <b>Email:</b> {config.COMPANY_EMAIL}<br/>
    <b>Website:</b> www.swiftfreightsolutions.com<br/>
    </para>
    """
    story.append(Paragraph(contact_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return output_path


if __name__ == "__main__":
    # Test PDF generation with map
    test_quote = {
        "quote_id": "QT-2025-001234",
        "total_cost": 3105.00,
        "breakdown": {
            "base_rate": 2200.00,
            "fuel_surcharge": 330.00,
            "liftgate_fee": 75.00,
            "insurance": 500.00,
            "climate_control_fee": 0.0
        },
        "transit_days": 2,
        "equipment_type": "dry_van",
        "valid_until": "2025-11-21T23:59:59Z",
        "terms": "Payment due upon delivery",
        "distance_miles": 162.5,
        "duration_hours": 2.7,
        "route_map_url": "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-s-a+00ff00(-95.3698,29.7604),pin-s-b+ff0000(-97.7431,30.2672)/-96.5565,29.9988,7/600x400?access_token=YOUR_MAPBOX_KEY"
    }
    
    test_shipment = {
        "origin": {"city": "Houston", "state": "TX", "zip": "77001"},
        "destination": {"city": "Austin", "state": "TX", "zip": "78701"},
        "cargo": {
            "weight_lbs": 400,
            "pieces": 4,
            "piece_type": "pallets",
            "dimensions": {"length": 44, "width": 40, "height": 60},
            "commodity": "electronics"
        },
        "special_services": ["liftgate"]
    }
    
    output = "/tmp/test_quote_with_map.pdf"
    generate_quote_pdf(test_quote, test_shipment, output)
    print(f"Test PDF generated: {output}")
