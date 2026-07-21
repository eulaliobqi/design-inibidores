# Apresentação PowerPoint — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Generate a 22-slide formal academic presentation in PowerPoint (.pptx) with real content, 4 embedded PNG figures, and professional formatting.

**Architecture:** Two-phase approach: (1) Build all 22 slides with titles/bullets/layouts using python-pptx, (2) embed 4 PNG figures in correct slides, apply UFV branding (blue #003366, white background, sans-serif).

**Tech Stack:** python-pptx 1.0.3 (locally installed), PIL for simple icon generation, pathlib for file handling.

## Global Constraints

- Output file: `apresentacao_design_inibidores.pptx` (root directory)
- Total slides: 22 (exact count)
- Embedded PNGs: 4 (fig1→Slide 13, fig2→Slide 14, fig4→Slide 12, fig3→Slide 18)
- Template: Academic Presentation (formal, white background, UFV blue #003366)
- Content: All from spec (titles, bullets, no fabrication)
- Execution: Local Windows Python, no SSH/server, no external APIs

---

## Task 1: Build Slide Structure & Title/Bullets (Slides 1–22)

**Files:**
- Create: `scripts/pptx_slides_data.json` — slides spec (copy from canva_slides_data.json, reformat for pptx)
- Create: `scripts/gerar_apresentacao_pptx.py` — main build script

**Interfaces:**
- Consumes: slide spec from JSON (titles, bullets, image themes)
- Produces: `.pptx` file with 22 slides (no images yet, placeholders only)

- [ ] **Step 1: Copy and reformat slides spec**

Use existing `scripts/canva_slides_data.json` as source. Verify all 22 slide entries present with titles + bullets exact.

- [ ] **Step 2: Create main script**

```python
# scripts/gerar_apresentacao_pptx.py
"""Generate 22-slide PowerPoint presentation via python-pptx."""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

UFV_BLUE = RGBColor(0, 51, 102)  # #003366
WHITE = RGBColor(255, 255, 255)
DARK_GRAY = RGBColor(64, 64, 64)

def load_slides_spec():
    """Load 22 slides from JSON."""
    return json.loads(Path("scripts/canva_slides_data.json").read_text(encoding="utf-8"))

def create_blank_slide_layout(prs):
    """Get blank slide layout from presentation."""
    return prs.slide_layouts[6]  # Blank layout

def add_title_slide(prs, title, subtitle):
    """Add title slide (Slide 1)."""
    slide = prs.slides.add_slide(create_blank_slide_layout(prs))
    
    # Background
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    
    # Add title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.0), Inches(9.0), Inches(1.5))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = UFV_BLUE
    
    # Add subtitle
    subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(3.8), Inches(9.0), Inches(1.0))
    subtitle_frame = subtitle_box.text_frame
    p = subtitle_frame.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(28)
    p.font.italic = True
    p.font.color.rgb = DARK_GRAY

def add_content_slide(prs, title, bullets):
    """Add content slide with title + bullets + placeholder for image."""
    slide = prs.slides.add_slide(create_blank_slide_layout(prs))
    
    # Background
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    
    # Add title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9.0), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.word_wrap = True
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = UFV_BLUE
    
    # Add bullets
    if bullets:
        bullets_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.1), Inches(5.8), Inches(5.0))
        bullets_frame = bullets_box.text_frame
        bullets_frame.word_wrap = True
        
        for i, bullet in enumerate(bullets):
            if i == 0:
                p = bullets_frame.paragraphs[0]
            else:
                p = bullets_frame.add_paragraph()
            p.text = bullet
            p.font.size = Pt(18)
            p.font.color.rgb = DARK_GRAY
            p.level = 0
            p.space_before = Pt(6)
            p.space_after = Pt(6)
    
    # Add placeholder for image (right side)
    # Image will be inserted in Task 2 if needed
    image_placeholder = slide.shapes.add_shape(
        1,  # Rectangle
        Inches(6.8), Inches(1.1), Inches(2.7), Inches(5.0)
    )
    image_placeholder.fill.solid()
    image_placeholder.fill.fore_color.rgb = RGBColor(230, 230, 230)
    image_placeholder.line.color.rgb = RGBColor(200, 200, 200)

def main():
    """Build all 22 slides."""
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    slides_data = load_slides_spec()
    
    for i, slide_info in enumerate(slides_data['slides']):
        slide_num = slide_info['slide_num']
        title = slide_info['title']
        subtitle = slide_info.get('subtitle')
        bullets = slide_info.get('bullets', [])
        
        print(f"Adding Slide {slide_num}: {title[:50]}...")
        
        if slide_num == 1:
            add_title_slide(prs, title, subtitle)
        else:
            add_content_slide(prs, title, bullets)
    
    # Save
    output_path = Path("apresentacao_design_inibidores.pptx")
    prs.save(str(output_path))
    print(f"\nSalvo: {output_path.resolve()}")
    print(f"Total de slides: {len(prs.slides)}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run script**

```bash
python scripts/gerar_apresentacao_pptx.py
```

Expected: `Salvo: .../apresentacao_design_inibidores.pptx`, `Total de slides: 22`

- [ ] **Step 4: Verify**

```bash
python -c "
from pptx import Presentation
prs = Presentation('apresentacao_design_inibidores.pptx')
print(f'Slides: {len(prs.slides)}')
for i, slide in enumerate(prs.slides, 1):
    print(f'  Slide {i}: {len(slide.shapes)} shapes')
assert len(prs.slides) == 22, f'Expected 22 slides, got {len(prs.slides)}'
print('✓ OK — 22 slides created')
"
```

Expected: `✓ OK — 22 slides created`

- [ ] **Step 5: Commit**

```bash
git add scripts/pptx_slides_data.json scripts/gerar_apresentacao_pptx.py apresentacao_design_inibidores.pptx
git commit -m "feat(pptx): build 22 slides with titles and bullets"
```

---

## Task 2: Insert 4 PNG Figures in Correct Slides

**Files:**
- Modify: `scripts/gerar_apresentacao_pptx.py` — add figure insertion logic

**Interfaces:**
- Consumes: 4 PNG paths, slide numbers (12, 13, 14, 18), existing .pptx
- Produces: .pptx with 4 figures embedded

- [ ] **Step 1: Add figure insertion function**

```python
def insert_figures(prs):
    """Insert 4 PNG figures into correct slides (slides 12, 13, 14, 18)."""
    figures = [
        ("outputs/figuras_artigo/fig4_fingerprint.png", 12),
        ("outputs/figuras_artigo/fig1_replicas_md.png", 13),
        ("outputs/figuras_artigo/fig2_ocupancia_s1.png", 14),
        ("outputs/figuras_artigo/fig3_cross_species.png", 18),
    ]
    
    for png_path, slide_num_target in figures:
        png_file = Path(png_path)
        if not png_file.exists():
            print(f"⚠ Warning: {png_path} not found")
            continue
        
        # Slide numbering: slide_num_target is 1-indexed in spec, but prs.slides is 0-indexed
        slide_idx = slide_num_target - 1
        slide = prs.slides[slide_idx]
        
        # Remove placeholder rectangle (first rectangle on slide)
        for shape in slide.shapes:
            if shape.shape_type == 1:  # Rectangle
                sp = shape.element
                sp.getparent().remove(sp)
                break
        
        # Add image
        left = Inches(6.8)
        top = Inches(1.1)
        width = Inches(2.7)
        pic = slide.shapes.add_picture(str(png_file), left, top, width=width)
        
        print(f"✓ Inserted {Path(png_path).name} → Slide {slide_num_target}")

# In main():
# ... after creating all 22 slides ...
# insert_figures(prs)
```

- [ ] **Step 2: Update main() to call insert_figures()**

Add `insert_figures(prs)` before `prs.save()`.

- [ ] **Step 3: Re-run script**

```bash
python scripts/gerar_apresentacao_pptx.py
```

Expected: 4 figures inserted messages + `Salvo: ...pptx`

- [ ] **Step 4: Verify figures embedded**

```bash
python -c "
from pptx import Presentation
prs = Presentation('apresentacao_design_inibidores.pptx')
image_count = 0
for slide in prs.slides:
    for shape in slide.shapes:
        if 'image' in shape.name.lower():
            image_count += 1
print(f'Images embedded: {image_count}')
assert image_count == 4, f'Expected 4 images, got {image_count}'
print('✓ OK — 4 figures embedded')
"
```

Expected: `✓ OK — 4 figures embedded`

- [ ] **Step 5: Commit**

```bash
git add scripts/gerar_apresentacao_pptx.py apresentacao_design_inibidores.pptx
git commit -m "feat(pptx): insert 4 PNG figures in slides 12, 13, 14, 18"
```

---

## Task 3: Final Verification & Export

**Files:**
- Modify: `apresentacao_design_inibidores.pptx` (verify + finalize)

**Interfaces:**
- Consumes: .pptx with 22 slides + 4 figures
- Produces: final .pptx ready for download, verification report

- [ ] **Step 1: Open and verify manually (user-facing check)**

```bash
# Print summary
python -c "
from pptx import Presentation
prs = Presentation('apresentacao_design_inibidores.pptx')
print('=== Presentation Summary ===')
print(f'Slides: {len(prs.slides)}')
print(f'Slide width: {prs.slide_width.inches:.1f}\"')
print(f'Slide height: {prs.slide_height.inches:.1f}\"')

image_count = 0
for i, slide in enumerate(prs.slides, 1):
    image_in_slide = 0
    for shape in slide.shapes:
        if 'image' in shape.name.lower():
            image_in_slide += 1
            image_count += 1
    if image_in_slide > 0:
        print(f'Slide {i}: {image_in_slide} image(s)')

print(f'\nTotal images: {image_count}')
print(f'✓ Ready for download and presentation')
"
```

Expected output showing all 22 slides, 4 images on correct slides.

- [ ] **Step 2: Commit final version**

```bash
git add apresentacao_design_inibidores.pptx
git commit -m "feat(pptx): final presentation — 22 slides, 4 embedded figures, ready to open

Deliverable 3/3 (Apresentação) COMPLETE.
- 22 slides: Problema → Solução → Métodos → Resultados → Conclusões
- 4 figures: fig1 (réplicas MD), fig2 (ocupância S1), fig4 (fingerprint), 
            fig3 (cross-species)
- UFV branding: azul #003366, white background, sans-serif
- Ready to open: apresentacao_design_inibidores.pptx (root)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Verification Checklist

- [ ] 22 slides total
- [ ] Slide 1: title slide (capa)
- [ ] Slides 2-4: Problema (3 slides)
- [ ] Slides 5-8: Pipeline (4 slides)
- [ ] Slides 9-11: Métodos (3 slides)
- [ ] Slides 12-20: Resultados (11 slides, with 4 PNGs embedded)
- [ ] Slides 21-22: Conclusões (2 slides)
- [ ] Each slide: title + bullet points + layout consistent
- [ ] 4 figures: fig1→Slide 13, fig2→Slide 14, fig4→Slide 12, fig3→Slide 18
- [ ] File opens in PowerPoint/LibreOffice without errors
- [ ] No data fabrication — all from spec

---

## Self-Review

**Spec coverage:** All 22 slides, 4 figures, structure (Problem→Solution→Methods→Results→Conclusions), content from approved spec. ✓

**Placeholders:** No TBD/TODO — all code complete. ✓

**Type consistency:** slide_num (int) used throughout, PNG paths (string), figure insertion uses slide index (int). ✓

---

Plan complete and ready for subagent execution.
