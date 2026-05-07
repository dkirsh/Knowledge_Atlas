# Library Extension Proposal

## 1. Target Room Type and Closest Existing Entity

Target room type: library

Closest existing Infinigen entity: office

The current office entity already supports desks, chairs, shelving, and work-oriented layouts, making it the closest existing semantic category. However, it does not fully represent library-specific spatial organization, reading behavior, or bookshelf-dominated interiors.

## 2. Gap Analysis

A library differs from a standard office because it prioritizes:
- bookshelf density and navigation between shelves
- quiet reading and study zones
- large collections of books and media
- long-duration seated attention
- softer and more uniform lighting conditions
- circulation paths between stacks

The existing office entity focuses more on workstation density and workplace organization. It lacks controls for reading-oriented atmosphere, shelf-heavy layouts, and study-space acoustics.

## 3. Proposed Parameters

### bookshelf_density

Controls the amount of bookshelf coverage in the room.

Visual effects:
- wall coverage
- visual complexity
- navigation between shelves

Motivation:
Bookshelf density changes perceived information richness and enclosure.

---

### study_table_count

Controls the number of reading/study tables.

Visual effects:
- seating density
- collaborative vs individual study feel

Motivation:
Study-table count changes perceived social density and workspace affordances.

---

### seating_spacing

Controls spacing between chairs and study areas.

Visual effects:
- openness
- privacy
- crowding

Motivation:
Seating spacing affects perceived privacy and comfort.

---

### daylight_intensity

Controls daylight contribution from windows/skylights.

Visual effects:
- brightness
- visual comfort
- atmosphere

Motivation:
Lighting strongly affects reading comfort and sustained attention.

---

### ambient_noise_level

Controls simulated quietness vs socially active atmosphere.

Visual effects:
- occupancy density
- spacing
- social grouping

Motivation:
Libraries differ substantially in quiet-study vs collaborative-study atmosphere.

---

### bookshelf_height_scale

Controls bookshelf vertical scale.

Visual effects:
- enclosure
- ceiling visibility
- spatial compression

Motivation:
Tall shelving changes perceived enclosure and navigability.

## 4. Likely Implementation Hooks

Likely files to extend:

- `infinigen/core/tags.py`
- `infinigen_examples/constraints/home.py`
- `infinigen/core/constraints/example_solver/room/decorate.py`
- `infinigen/assets/objects/shelves/`
- `infinigen/assets/composition/material_assignments.py`

Potential reusable entities:
- OfficeChairFactory
- shelf-related factories
- table factories
- existing office layout constraints

## 5. Literature Backing

Kaplan & Kaplan (1989):
Environmental complexity and restorative environments influence attention and comfort.

Meyers-Levy & Zhu (2007):
Spatial openness and enclosure influence cognition and perception.

Ulrich (1991):
Interior environmental conditions affect stress reduction and perceived comfort.

Joye (2007):
Visual complexity and biophilic/interior environmental features influence psychological response.

## 6. Proposed JSON-Schema Fragment

```json
{
  "bookshelf_density": {
    "type": "number",
    "minimum": 0.0,
    "maximum": 1.0,
    "default": 0.7
  },
  "study_table_count": {
    "type": "integer",
    "minimum": 0,
    "maximum": 20,
    "default": 6
  },
  "seating_spacing": {
    "type": "number",
    "minimum": 0.5,
    "maximum": 3.0,
    "default": 1.5
  }
}