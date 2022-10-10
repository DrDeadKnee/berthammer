TABLE Unit
  -- unit id
  timestamp VARCHAR
  alliance VARCHAR
  faction VARCHAR
  unit_name VARCHAR
  -- profile
  points INTEGER
  roles VARCHAR
  base_size VARCHAR
  notes VARCHAR
  unit_size: INTEGER
  -- card
  move INTEGER
  save INTEGER
  wounds INTEGER
  bravery INTEGER
  -- common characteristics
  fly BOOLEAN
  mounted BOOLEAN

TABLE WEAPROFS
  -- unit id
  timestamp VARCHAR
  alliance VARCHAR
  faction VARCHAR
  unit_name VARCHAR
  -- profile
  weapon_name VARCHAR
  attk_type VARCHAR (MELEE // MISSILE)
  range INTEGER
  attacks INTEGER
  to_hit INTEGER
  to_wound INTEGER
  rend INTEGER
  damage INTEGER

TABLE DAMAGE
  -- unit id
  timestamp VARCHAR
  alliance VARCHAR
  faction VARCHAR
  unit_name VARCHAR
  -- dt
  wounds_suffered VARCHAR
  move INTEGER
  stat1_name VARCHAR
  stat1_value INTEGER
  stat2_name VARCHAR
  stat2_value INTEGER
  stat3_name VARCHAR
  stat3_value INTEGER
  stat4_name VARCHAR
  stat4_value INTEGER

TABLE ABILITIES
  -- unit id
  timestamp VARCHAR
  alliance VARCHAR
  faction VARCHAR
  unit_name VARCHAR
  -- abilities
  ability_name VARCHAR
  ability_desc VARCHAR (Long)
