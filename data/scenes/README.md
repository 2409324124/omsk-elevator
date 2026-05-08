# Scene Data

Place scene JSON files here.

The first-pass validator accepts either one scene object per file or a list of
scene objects. It currently checks:

- unique scene ids
- unique choice ids
- legal numeric `effects` keys
- legal `force_next_if` keys
- `force_next_if.scene` references an existing scene id
