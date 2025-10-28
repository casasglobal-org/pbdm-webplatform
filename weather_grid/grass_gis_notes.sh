# grass_gis_notes.sh
# Author: Luigi Ponti quartese gmail.com
# Copyright: (c) 2025 CASAS (Center for the Analysis of Sustainable Agricultural Systems, https://www.casasglobal.org/)
# SPDX-License-Identifier: GPL-3.0-or-later
# 2025-10-23

# Import grid extracted with netcdf_grid_extract.py to GRASS GIS
# latlong location
v.in.ascii input='/Users/luigi/Documents/maxtor/pending projects/CASAS object oriented models/McKnight/2025-07-26 pbdm web platform markus neteler/MPI-ESM1-2-HR_grid_tasmax.txt' output=nexgddp_v2_mpi_ESM1_2_HR_grid fs=tab skip=1 columns="x integer, y integer, lon double precision, lat double precision" x=3 y=4

# Add columns that will be populated with country/state codes.
v.db.addcolumn map=nexgddp_v2_mpi_ESM1_2_HR_grid columns="country varchar(10), state varchar(10)"

# Populate with country
v.what.vect map=nexgddp_v2_mpi_ESM1_2_HR_grid  column=country query_map="ne_50m_admin_0_countries_lakes" query_column=iso_a3 dmax=-1

# Populate with state
v.what.vect map=nexgddp_v2_mpi_ESM1_2_HR_grid  column=state query_map=ne_50m_admin_1_states_provinces_lakes query_column=postal dmax=12500

# See below example of how to add states or other admnistrative units
# based on another layer (here Mexico states).

# Add column for Mexico states.
v.db.addcolumn map=nexgddp_v2_mpi_ESM1_2_HR_grid  columns="mex_state varchar(10)"
# Populate with Mexico states
v.what.vect map=nexgddp_v2_mpi_ESM1_2_HR_grid  column=mex_state query_map="MEX_adm1@luigi" query_column=HASC_1

# Use temp file to be on the safe side
g.copy vect=nexgddp_v2_mpi_ESM1_2_HR_grid,nexgddp_v2_mpi_ESM1_2_HR_grid _tmp

# Put Mexico states into state column.
v.db.update map=nexgddp_v2_mpi_ESM1_2_HR_grid _tmp column=state qcolumn=mex_state where="state IS NULL"

# Exported SQLite table to nexgddp_v2_mpi_ESM1_2_HR_grid_sqlite_dump.txt
