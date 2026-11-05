# Generated module prerequisites; no recipes or scientific source edits.
CO_strat_pl.o: dao_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
CO_strat_pl_adj.o: adj_arrays_mod.o dao_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
JRATET.o: fjx_acet_mod.o
Kr85_mod.o: error_mod.o time_mod.o tracer_mod.o
RnPbBe_mod.o: dao_mod.o diag_mod.o directory_mod.o file_mod.o grid_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o tropopause_mod.o
a3_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o
a6_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o
acetone_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o grid_mod.o time_mod.o transfer_mod.o
adj_arrays_mod.o: bpch2_mod.o charpak_mod.o comode_mod.o critical_load_mod.o dao_mod.o directory_mod.o error_mod.o gckpp_adj_Global.o gckpp_adj_Parameters.o grid_mod.o htap_mod.o logical_adj_mod.o logical_mod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o m_netcdf_io_readattr.o regrid_a2a_mod.o time_mod.o tracer_mod.o tracerid_mod.o
aerosol_mod.o: bpch2_mod.o comode_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
aircraft_nox_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o pressure_mod.o time_mod.o
anthroems.o: edgar_mod.o future_emissions_mod.o geia_mod.o grid_mod.o logical_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
arctas_ship_emiss_mod.o: bpch2_mod.o directory_mod.o error_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o tracer_mod.o tracerid_mod.o
atom_obs_mod.o: adj_arrays_mod.o checkpt_mod.o comode_mod.o dao_mod.o diag_mod.o grid_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
benchmark_mod.o: bpch2_mod.o file_mod.o time_mod.o tracer_mod.o tracerid_mod.o
biofuel_mod.o: bpch2_mod.o bravo_mod.o cac_anthro_mod.o dao_mod.o diag_mod.o directory_mod.o emep_mod.o epa_nei_mod.o error_mod.o future_emissions_mod.o logical_mod.o streets_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
biomass_mod.o: diag_mod.o error_mod.o gc_biomass_mod.o gfed2_biomass_mod.o gfed3_biomass_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o
boxvl.o: dao_mod.o
bpch2_mod.o: error_mod.o file_mod.o julday_mod.o
bravo_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracerid_mod.o transfer_mod.o
c2h6_mod.o: biofuel_mod.o biomass_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o geia_mod.o global_oh_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
cac_anthro_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
calcrate.o: adj_arrays_mod.o comode_mod.o dao_mod.o diag_mod.o drydep_mod.o error_mod.o gckpp_adj_Global.o grid_mod.o logical_adj_mod.o pbl_mix_mod.o planeflight_mod.o tracer_mod.o tracerid_mod.o
calcrate_adj.o: adj_arrays_mod.o comode_mod.o drydep_mod.o error_mod.o gckpp_adj_Global.o logical_adj_mod.o pbl_mix_mod.o
carbon_adj_mod.o: adj_arrays_mod.o carbon_mod.o dao_mod.o diag_mod.o drydep_mod.o error_mod.o gfed2_biomass_mod.o global_no3_mod.o global_o3_mod.o global_oh_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pbl_mix_mod.o time_mod.o tracer_mod.o tracerid_mod.o
carbon_mod.o: adj_arrays_mod.o biomass_mod.o bpch2_mod.o comode_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o error_mod.o file_mod.o future_emissions_mod.o gfed2_biomass_mod.o gfed3_biomass_mod.o global_no3_mod.o global_o3_mod.o global_oh_mod.o grid_mod.o htap_mod.o logical_adj_mod.o logical_mod.o megan_mod.o pbl_mix_mod.o pressure_mod.o rcp_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
ch3i_mod.o: biofuel_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_pl_mod.o directory_mod.o error_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o uvalbedo_mod.o
checkpoint_mod.o: bpch2_mod.o comode_mod.o dao_mod.o directory_adj_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o unix_cmds_mod.o
checkpt_mod.o: adj_arrays_mod.o bpch2_mod.o charpak_mod.o comode_mod.o diag_mod.o directory_adj_mod.o error_mod.o file_mod.o gckpp_adj_Global.o grid_mod.o logical_adj_mod.o logical_mod.o megan_mod.o restart_mod.o time_mod.o tracer_mod.o tracerid_mod.o unix_cmds_mod.o
chemdr.o: adj_arrays_mod.o aerosol_mod.o chemistry_mod.o comode_mod.o dao_mod.o diag_oh_mod.o diag_pl_mod.o drydep_mod.o dust_mod.o error_mod.o future_emissions_mod.o gckpp_adj_Global.o grid_mod.o input_adj_mod.o logical_adj_mod.o logical_mod.o planeflight_mod.o restart_mod.o strat_chem_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o uvalbedo_mod.o
chemdr_adj.o: adj_arrays_mod.o aerosol_mod.o checkpt_mod.o chemistry_mod.o comode_mod.o dao_mod.o diag_oh_mod.o diag_pl_mod.o drydep_mod.o dust_mod.o error_mod.o future_emissions_mod.o gckpp_adj_Global.o grid_mod.o logical_adj_mod.o logical_mod.o planeflight_mod.o restart_mod.o strat_chem_adj_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o uvalbedo_mod.o
chemistry_adj_mod.o: Kr85_mod.o RnPbBe_mod.o acetone_mod.o adj_arrays_mod.o aerosol_mod.o c2h6_mod.o carbon_adj_mod.o carbon_mod.o ch3i_mod.o dao_mod.o drydep_mod.o dust_adj_mod.o dust_mod.o error_mod.o global_ch4_adj_mod.o global_ch4_mod.o h2_hd_mod.o hcn_ch3cn_mod.o isoropiaII_adj_mod.o logical_adj_mod.o logical_mod.o mercury_mod.o optdepth_mod.o rpmares_adj_mod.o rpmares_mod.o seasalt_mod.o sulfate_adj_mod.o sulfate_mod.o tagged_co_adj_mod.o tagged_ox_adj_mod.o tagged_ox_mod.o time_mod.o tracer_mod.o tracerid_mod.o
chemistry_mod.o: Kr85_mod.o RnPbBe_mod.o acetone_mod.o adj_arrays_mod.o aerosol_mod.o c2h6_mod.o carbon_mod.o ch3i_mod.o comode_mod.o dao_mod.o drydep_mod.o dust_mod.o error_mod.o gckpp_adj_Global.o gckpp_adj_Initialize.o gckpp_adj_Integrator.o gckpp_adj_Monitor.o gckpp_adj_Parameters.o gckpp_adj_Rates.o gckpp_adj_Util.o global_ch4_mod.o h2_hd_mod.o hcn_ch3cn_mod.o isoropiaII_adj_mod.o logical_adj_mod.o logical_mod.o mercury_mod.o optdepth_mod.o rpmares_mod.o seasalt_mod.o sulfate_mod.o tagged_co_mod.o tagged_ox_mod.o time_mod.o tracer_mod.o tracerid_mod.o
cleanup.o: acetone_mod.o aerosol_mod.o aircraft_nox_mod.o arctas_ship_emiss_mod.o biofuel_mod.o biomass_mod.o bravo_mod.o c2h6_mod.o cac_anthro_mod.o carbon_mod.o co2_mod.o comode_mod.o dao_mod.o diag03_mod.o diag04_mod.o diag41_mod.o diag50_mod.o diag51_mod.o diag51b_mod.o diag51c_mod.o diag51d_mod.o diag_mod.o diag_oh_mod.o diag_pl_mod.o drydep_mod.o dust_dead_mod.o dust_mod.o edgar_mod.o emep_mod.o epa_nei_mod.o error_mod.o gc_biomass_mod.o gfed2_biomass_mod.o gfed3_biomass_mod.o global_ch4_mod.o global_hno3_mod.o global_no3_mod.o global_nox_mod.o global_o1d_mod.o global_oh_mod.o h2_hd_mod.o hcn_ch3cn_mod.o icoads_ship_mod.o lai_mod.o lightning_nox_mod.o megan_mod.o mercury_mod.o ocean_mercury_mod.o pbl_mix_mod.o pjc_pfix_mod.o planeflight_mod.o pressure_mod.o rcp_mod.o regrid_1x1_mod.o retro_mod.o seasalt_mod.o sulfate_mod.o tagged_co_mod.o toms_mod.o tpcore_fvdas_mod.o tpcore_geos5_window_mod.o tpcore_geosfp_window_mod.o tracer_mod.o transport_mod.o tropopause_mod.o uvalbedo_mod.o vistas_anthro_mod.o wetscav_mod.o
cleanup_adj.o: adj_arrays_mod.o global_ch4_adj_mod.o population_mod.o
co2_adj_mod.o: adj_arrays_mod.o biomass_mod.o co2_mod.o grid_mod.o logical_adj_mod.o logical_mod.o time_mod.o tracer_mod.o
co2_mod.o: adj_arrays_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag04_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o regrid_1x1_mod.o time_mod.o tracer_mod.o transfer_mod.o
comode_mod.o: error_mod.o tracer_mod.o
convection_adj_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o diag_mod.o error_mod.o fvdas_convect_adj_mod.o grid_mod.o logical_adj_mod.o logical_mod.o ocean_mercury_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
convection_mod.o: adj_arrays_mod.o dao_mod.o diag_mod.o error_mod.o fvdas_convect_mod.o gc_type_mod.o gcap_convect_mod.o grid_mod.o logical_adj_mod.o logical_mod.o ocean_mercury_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
critical_load_mod.o: bpch2_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o netcdf_util_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
dao_mod.o: error_mod.o grid_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o
diag03_mod.o: bpch2_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o tracerid_mod.o
diag04_mod.o: bpch2_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o
diag1.o: dao_mod.o diag_mod.o grid_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag3.o: biofuel_mod.o biomass_mod.o bpch2_mod.o diag03_mod.o diag04_mod.o diag41_mod.o diag42_mod.o diag56_mod.o diag59_mod.o diag_mod.o diag_pl_mod.o drydep_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
diag41_mod.o: bpch2_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o time_mod.o
diag42_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
diag48_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
diag49_mod.o: bpch2_mod.o checkpt_mod.o dao_mod.o diag_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
diag50_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag51_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag51b_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag51c_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag51d_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
diag56_mod.o: bpch2_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o
diag59_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
diag_2pm.o: diag_mod.o time_mod.o tropopause_mod.o
diag_oh_mod.o: comode_mod.o error_mod.o logical_mod.o tracer_mod.o tracerid_mod.o
diag_pl_mod.o: bpch2_mod.o charpak_mod.o comode_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o tracer_mod.o tracerid_mod.o
diagoh.o: diag_mod.o
drydep_mod.o: comode_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o pbl_mix_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
dust_adj_mod.o: adj_arrays_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o dust_dead_mod.o dust_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
dust_dead_mod.o: bpch2_mod.o dao_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o transfer_mod.o
dust_mod.o: adj_arrays_mod.o bpch2_mod.o comode_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o dust_dead_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
edgar_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o regrid_a2a_mod.o scale_anthro_mod.o time_mod.o
emep_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
emf_scale.o: tracerid_mod.o
emfossil.o: bravo_mod.o c2h6_mod.o cac_anthro_mod.o dao_mod.o diag49_mod.o diag_mod.o edgar_mod.o emep_mod.o epa_nei_mod.o grid_mod.o htap_mod.o icoads_ship_mod.o logical_mod.o nei2005_anthro_mod.o nei2008_anthro_mod.o rcp_mod.o retro_mod.o streets_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o vistas_anthro_mod.o
emisop.o: dao_mod.o
emisop_grass.o: dao_mod.o
emisop_mb.o: dao_mod.o
emissdr.o: acetone_mod.o aircraft_nox_mod.o biofuel_mod.o dao_mod.o diag49_mod.o diag_mod.o grid_mod.o htap_mod.o lightning_nox_mod.o logical_mod.o megan_mod.o rcp_mod.o time_mod.o tracer_mod.o tracerid_mod.o
emissions_adj_mod.o: Kr85_mod.o RnPbBe_mod.o adj_arrays_mod.o arctas_ship_emiss_mod.o biofuel_mod.o biomass_mod.o bravo_mod.o c2h6_mod.o cac_anthro_mod.o carbon_adj_mod.o carbon_mod.o ch3i_mod.o co2_adj_mod.o dust_adj_mod.o dust_mod.o edgar_mod.o emep_mod.o epa_nei_mod.o error_mod.o global_ch4_adj_mod.o global_ch4_mod.o h2_hd_mod.o hcn_ch3cn_mod.o htap_mod.o icoads_ship_mod.o logical_mod.o nei2005_anthro_mod.o nei2008_anthro_mod.o seasalt_mod.o streets_anthro_mod.o sulfate_adj_mod.o sulfate_mod.o tagged_co_adj_mod.o time_mod.o tracer_mod.o vistas_anthro_mod.o
emissions_mod.o: Kr85_mod.o RnPbBe_mod.o arctas_ship_emiss_mod.o biomass_mod.o bravo_mod.o c2h6_mod.o cac_anthro_mod.o carbon_mod.o ch3i_mod.o co2_mod.o dust_mod.o edgar_mod.o emep_mod.o epa_nei_mod.o error_mod.o global_ch4_mod.o h2_hd_mod.o hcn_ch3cn_mod.o htap_mod.o icoads_ship_mod.o logical_mod.o mercury_mod.o nei2005_anthro_mod.o nei2008_anthro_mod.o paranox_mod.o rcp_mod.o retro_mod.o seasalt_mod.o streets_anthro_mod.o sulfate_mod.o tagged_co_mod.o time_mod.o tracer_mod.o vistas_anthro_mod.o
epa_nei_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o future_emissions_mod.o grid_mod.o logical_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
fast_j.o: dao_mod.o error_mod.o grid_mod.o pressure_mod.o time_mod.o toms_mod.o
fertadd.o: grid_mod.o logical_mod.o time_mod.o
file_mod.o: error_mod.o
fjfunc.o: error_mod.o
future_emissions_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o transfer_mod.o
fvdas_convect_mod.o: diag_mod.o grid_mod.o logical_mod.o ocean_mercury_mod.o pressure_mod.o tracer_mod.o tracerid_mod.o
gamap_mod.o: adj_arrays_mod.o charpak_mod.o diag03_mod.o diag04_mod.o diag41_mod.o diag42_mod.o diag48_mod.o diag49_mod.o diag50_mod.o diag51_mod.o diag56_mod.o diag59_mod.o diag_pl_mod.o drydep_mod.o error_mod.o file_mod.o gckpp_adj_Global.o gckpp_adj_Util.o logical_adj_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
gasconc.o: comode_mod.o dao_mod.o drydep_mod.o logical_mod.o pressure_mod.o time_mod.o tropopause_mod.o
gc_biomass_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
gcap_convect_mod.o: dao_mod.o diag_mod.o grid_mod.o pressure_mod.o
gcap_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o
gckpp_adj_Function.o: gckpp_adj_Parameters.o
gckpp_adj_Global.o: gckpp_adj_Parameters.o
gckpp_adj_Hessian.o: gckpp_adj_HessianSP.o gckpp_adj_Parameters.o
gckpp_adj_Initialize.o: gckpp_adj_Global.o gckpp_adj_Monitor.o gckpp_adj_Parameters.o gckpp_adj_Util.o
gckpp_adj_Integrator.o: gckpp_adj_Function.o gckpp_adj_Global.o gckpp_adj_Hessian.o gckpp_adj_Jacobian.o gckpp_adj_LinearAlgebra.o gckpp_adj_Parameters.o gckpp_adj_Precision.o gckpp_adj_Rates.o gckpp_adj_Stoichiom.o gckpp_adj_Util.o logical_adj_mod.o
gckpp_adj_Jacobian.o: gckpp_adj_JacobianSP.o gckpp_adj_Parameters.o
gckpp_adj_LinearAlgebra.o: gckpp_adj_JacobianSP.o gckpp_adj_Parameters.o
gckpp_adj_Model.o: gckpp_adj_Function.o gckpp_adj_Global.o gckpp_adj_Hessian.o gckpp_adj_Integrator.o gckpp_adj_Jacobian.o gckpp_adj_LinearAlgebra.o gckpp_adj_Monitor.o gckpp_adj_Parameters.o gckpp_adj_Precision.o gckpp_adj_Rates.o gckpp_adj_Stoichiom.o gckpp_adj_Util.o
gckpp_adj_Parameters.o: gckpp_adj_Precision.o
gckpp_adj_Rates.o: comode_mod.o gckpp_adj_Global.o gckpp_adj_Monitor.o gckpp_adj_Parameters.o
gckpp_adj_Stoichiom.o: gckpp_adj_Parameters.o gckpp_adj_StoichiomSP.o
gckpp_adj_StoichiomSP.o: gckpp_adj_Precision.o
gckpp_adj_Util.o: adj_arrays_mod.o gckpp_adj_Global.o gckpp_adj_Monitor.o gckpp_adj_Parameters.o logical_adj_mod.o
geia_mod.o: bpch2_mod.o directory_mod.o file_mod.o grid_mod.o time_mod.o
geos_chem_adj_mod.o: a3_read_mod.o a6_read_mod.o adj_arrays_mod.o benchmark_mod.o bpch2_mod.o carbon_mod.o checkpoint_mod.o checkpt_mod.o chemistry_adj_mod.o comode_mod.o convection_adj_mod.o convection_mod.o dao_mod.o diag41_mod.o diag42_mod.o diag48_mod.o diag49_mod.o diag50_mod.o diag51_mod.o diag_mod.o diag_oh_mod.o directory_adj_mod.o drydep_mod.o emissions_adj_mod.o emissions_mod.o error_mod.o file_mod.o gcap_read_mod.o gckpp_adj_Global.o geos_chem_mod.o geosfp_read_mod.o global_ch4_mod.o grid_mod.o gwet_read_mod.o i6_read_mod.o improve_bc_mod.o input_mod.o lai_mod.o lightning_nox_mod.o logical_adj_mod.o logical_mod.o megan_mod.o ocean_mercury_mod.o pbl_mix_adj_mod.o pbl_mix_mod.o planeflight_mod.o population_mod.o pressure_mod.o restart_mod.o time_mod.o tracer_mod.o tracerid_mod.o transport_mod.o tropopause_mod.o upbdflx_adj_mod.o upbdflx_mod.o uvalbedo_mod.o weak_constraint_mod.o wetscav_adj_mod.o wetscav_mod.o xtra_read_mod.o
geos_chem_mod.o: a3_read_mod.o a6_read_mod.o adj_arrays_mod.o atom_obs_mod.o benchmark_mod.o carbon_mod.o checkpt_mod.o chemistry_mod.o comode_mod.o convection_mod.o dao_mod.o diag41_mod.o diag42_mod.o diag48_mod.o diag49_mod.o diag50_mod.o diag51_mod.o diag51b_mod.o diag51c_mod.o diag51d_mod.o diag59_mod.o diag_mod.o diag_oh_mod.o drydep_mod.o emissions_mod.o error_mod.o file_mod.o gcap_read_mod.o geosfp_read_mod.o global_ch4_mod.o grid_mod.o gwet_read_mod.o hippo_mod.o i6_read_mod.o improve_bc_mod.o input_mod.o lai_mod.o lightning_nox_mod.o linoz_mod.o logical_adj_mod.o logical_mod.o megan_mod.o ocean_mercury_mod.o pbl_mix_mod.o planeflight_mod.o pressure_mod.o restart_mod.o time_mod.o tracer_mod.o tracerid_mod.o transport_mod.o tropopause_mod.o uvalbedo_mod.o weak_constraint_mod.o wetscav_mod.o xtra_read_mod.o
geosfp_read_mod.o: dao_mod.o diag_mod.o directory_mod.o error_mod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o time_mod.o transfer_mod.o
get_global_ch4.o: future_emissions_mod.o logical_mod.o
getifsun.o: comode_mod.o
gfed2_biomass_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o future_emissions_mod.o grid_mod.o julday_mod.o logical_mod.o regrid_1x1_mod.o time_mod.o tracer_mod.o
gfed3_biomass_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o future_emissions_mod.o grid_mod.o julday_mod.o logical_mod.o time_mod.o tracer_mod.o
global_ch4_adj_mod.o: adj_arrays_mod.o bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o global_ch4_mod.o global_oh_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o transfer_mod.o
global_ch4_mod.o: adj_arrays_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_oh_mod.o diag_pl_mod.o directory_mod.o error_mod.o file_mod.o global_oh_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o transfer_mod.o
global_hno3_mod.o: bpch2_mod.o dao_mod.o directory_mod.o error_mod.o tracer_mod.o transfer_mod.o
global_no3_mod.o: bpch2_mod.o directory_mod.o error_mod.o transfer_mod.o
global_nox_mod.o: bpch2_mod.o directory_mod.o error_mod.o transfer_mod.o unix_cmds_mod.o
global_o1d_mod.o: bpch2_mod.o directory_mod.o error_mod.o transfer_mod.o
global_o3_mod.o: bpch2_mod.o directory_mod.o error_mod.o transfer_mod.o
global_oh_mod.o: bpch2_mod.o directory_mod.o error_mod.o time_mod.o tracer_mod.o transfer_mod.o
grid_mod.o: error_mod.o
gwet_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o
h2_hd_mod.o: biofuel_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o error_mod.o geia_mod.o global_nox_mod.o global_o1d_mod.o global_oh_mod.o grid_mod.o logical_mod.o pressure_mod.o scale_anthro_mod.o tagged_co_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
hcn_ch3cn_mod.o: biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o geia_mod.o global_oh_mod.o grid_mod.o logical_mod.o pbl_mix_mod.o time_mod.o transfer_mod.o
hippo_mod.o: adj_arrays_mod.o comode_mod.o dao_mod.o diag_mod.o grid_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
htap_mod.o: directory_mod.o error_mod.o grid_mod.o logical_mod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o m_netcdf_io_readattr.o regrid_a2a_mod.o time_mod.o tracer_mod.o tracerid_mod.o
i6_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o
icoads_ship_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
improve_bc_mod.o: bpch2_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o time_mod.o
initialize.o: diag03_mod.o diag04_mod.o diag41_mod.o diag42_mod.o diag56_mod.o diag59_mod.o diag_mod.o diag_pl_mod.o error_mod.o logical_mod.o time_mod.o
inphot.o: error_mod.o file_mod.o
input_adj_mod.o: adj_arrays_mod.o charpak_mod.o critical_load_mod.o directory_adj_mod.o drydep_mod.o error_mod.o file_mod.o gamap_mod.o gckpp_adj_Global.o grid_mod.o input_mod.o logical_adj_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o unix_cmds_mod.o weak_constraint_mod.o wetscav_mod.o
input_mod.o: benchmark_mod.o biofuel_mod.o biomass_mod.o bpch2_mod.o charpak_mod.o diag03_mod.o diag04_mod.o diag41_mod.o diag42_mod.o diag48_mod.o diag49_mod.o diag50_mod.o diag51_mod.o diag51b_mod.o diag51c_mod.o diag51d_mod.o diag56_mod.o diag59_mod.o diag_oh_mod.o diag_pl_mod.o directory_mod.o drydep_mod.o error_mod.o file_mod.o future_emissions_mod.o gamap_mod.o grid_mod.o htap_mod.o julday_mod.o logical_mod.o mercury_mod.o ocean_mercury_mod.o planeflight_mod.o rcp_mod.o restart_mod.o time_mod.o tpcore_bc_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o transport_mod.o unix_cmds_mod.o upbdflx_mod.o wetscav_mod.o
inv_hessian_mod.o: adj_arrays_mod.o bpch2_mod.o directory_adj_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o restart_mod.o time_mod.o tracer_mod.o
inverse_driver.o: a3_read_mod.o a6_read_mod.o adj_arrays_mod.o checkpt_mod.o error_mod.o file_mod.o geos_chem_adj_mod.o geos_chem_mod.o gwet_read_mod.o i6_read_mod.o input_adj_mod.o input_mod.o inv_hessian_mod.o inverse_mod.o logical_adj_mod.o logical_mod.o weak_constraint_mod.o
inverse_mod.o: adj_arrays_mod.o bpch2_mod.o directory_adj_mod.o directory_mod.o error_mod.o file_mod.o gckpp_adj_Global.o geos_chem_adj_mod.o grid_mod.o logical_adj_mod.o logical_mod.o restart_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
isoropiaII_adj_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o error_mod.o global_hno3_mod.o logical_adj_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
jsparse.o: comode_mod.o error_mod.o
ksparse.o: error_mod.o
lai_mod.o: bpch2_mod.o directory_mod.o error_mod.o regrid_1x1_mod.o regrid_a2a_mod.o time_mod.o transfer_mod.o
lightning_nox_mod.o: bpch2_mod.o checkpt_mod.o dao_mod.o diag56_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pressure_mod.o time_mod.o transfer_mod.o
linoz_adj_mod.o: adj_arrays_mod.o checkpoint_mod.o dao_mod.o error_mod.o grid_mod.o logical_adj_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
linoz_mod.o: adj_arrays_mod.o checkpoint_mod.o dao_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_adj_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
lump.o: comode_mod.o tracerid_mod.o
lump_adj.o: comode_mod.o tracerid_mod.o
m_netcdf_io_close.o: m_do_err_out.o
m_netcdf_io_create.o: m_do_err_out.o
m_netcdf_io_define.o: m_do_err_out.o
m_netcdf_io_get_dimlen.o: m_do_err_out.o
m_netcdf_io_handle_err.o: m_do_err_out.o
m_netcdf_io_open.o: m_do_err_out.o
m_netcdf_io_read.o: m_do_err_out.o
m_netcdf_io_readattr.o: m_do_err_out.o
m_netcdf_io_write.o: m_do_err_out.o
megan_mod.o: a3_read_mod.o bpch2_mod.o directory_mod.o error_mod.o file_mod.o geosfp_read_mod.o grid_mod.o julday_mod.o lai_mod.o logical_adj_mod.o logical_mod.o regrid_1x1_mod.o regrid_a2a_mod.o time_mod.o
mercury_mod.o: bpch2_mod.o dao_mod.o diag03_mod.o diag_mod.o directory_mod.o drydep_mod.o error_mod.o global_o3_mod.o global_oh_mod.o grid_mod.o logical_mod.o ocean_mercury_mod.o pbl_mix_mod.o pressure_mod.o regrid_1x1_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
ndxx_setup.o: biofuel_mod.o biomass_mod.o diag49_mod.o diag_mod.o diag_oh_mod.o drydep_mod.o error_mod.o logical_mod.o planeflight_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
nei2005_anthro_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
nei2008_anthro_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o m_netcdf_io_readattr.o regrid_a2a_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
netcdf_util_mod.o: error_mod.o
ocean_mercury_mod.o: bpch2_mod.o dao_mod.o diag03_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
ohsave.o: comode_mod.o diag_mod.o tracerid_mod.o
optdepth_mod.o: diag_mod.o
paranox_adj_mod.o: dao_mod.o error_mod.o paranox_mod.o
paranox_mod.o: dao_mod.o directory_mod.o error_mod.o file_mod.o inquireMod.o time_mod.o
partition.o: adj_arrays_mod.o checkpt_mod.o comode_mod.o error_mod.o logical_adj_mod.o tracerid_mod.o
partition_adj.o: checkpt_mod.o comode_mod.o error_mod.o tracerid_mod.o
pbl_mix_adj_mod.o: adj_arrays_mod.o dao_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o
pbl_mix_mod.o: adj_arrays_mod.o dao_mod.o diag_mod.o error_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pressure_mod.o time_mod.o tracer_mod.o
physproc.o: comode_mod.o time_mod.o
pjc_pfix_geos5_window_mod.o: error_mod.o grid_mod.o pressure_mod.o
pjc_pfix_geosfp_window_mod.o: error_mod.o grid_mod.o pressure_mod.o
pjc_pfix_mod.o: error_mod.o grid_mod.o pressure_mod.o
planeflight_mod.o: bpch2_mod.o comode_mod.o dao_mod.o error_mod.o file_mod.o pressure_mod.o time_mod.o tracer_mod.o tropopause_mod.o
population_mod.o: adj_arrays_mod.o bpch2_mod.o checkpt_mod.o dao_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o
precipfrac.o: dao_mod.o grid_mod.o
pressure_mod.o: error_mod.o
pulsing.o: time_mod.o
rcp_mod.o: aircraft_nox_mod.o bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
rd_aod.o: error_mod.o file_mod.o
rdisopt.o: directory_mod.o file_mod.o
rdlai.o: grid_mod.o
rdland.o: directory_mod.o error_mod.o grid_mod.o logical_mod.o
rdlight.o: directory_mod.o file_mod.o
rdmonot.o: directory_mod.o file_mod.o
rdsoil.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o time_mod.o
readchem.o: diag_pl_mod.o drydep_mod.o error_mod.o
reader.o: error_mod.o file_mod.o logical_adj_mod.o time_mod.o tracer_mod.o
readlai.o: directory_mod.o file_mod.o logical_mod.o
regrid_1x1_mod.o: charpak_mod.o error_mod.o grid_mod.o
regrid_a2a_mod.o: file_mod.o grid_mod.o inquireMod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o m_netcdf_io_readattr.o
restart_mod.o: bpch2_mod.o charpak_mod.o comode_mod.o dao_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o
retro_mod.o: bpch2_mod.o directory_mod.o error_mod.o file_mod.o future_emissions_mod.o grid_mod.o logical_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o
routines.o: logical_adj_mod.o
rpmares_adj_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o error_mod.o logical_adj_mod.o rpmares_mod.o tracerid_mod.o tropopause_mod.o
rpmares_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o error_mod.o global_hno3_mod.o logical_adj_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
ruralbox.o: comode_mod.o pressure_mod.o tropopause_mod.o
scale_anthro_mod.o: bpch2_mod.o directory_mod.o file_mod.o regrid_1x1_mod.o regrid_a2a_mod.o
schem.o: bpch2_mod.o dao_mod.o directory_mod.o error_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
schem_adj.o: adj_arrays_mod.o bpch2_mod.o dao_mod.o directory_mod.o error_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
seasalt_mod.o: dao_mod.o diag_mod.o drydep_mod.o error_mod.o grid_mod.o logical_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
set_prof.o: adj_arrays_mod.o toms_mod.o
setbase.o: grid_mod.o time_mod.o
setemdep.o: drydep_mod.o tracer_mod.o tracerid_mod.o
setemis.o: adj_arrays_mod.o aircraft_nox_mod.o biofuel_mod.o biomass_mod.o comode_mod.o dao_mod.o diag_mod.o drydep_mod.o edgar_mod.o emep_mod.o emissions_mod.o grid_mod.o icoads_ship_mod.o lightning_nox_mod.o logical_mod.o paranox_mod.o pbl_mix_mod.o pressure_mod.o rcp_mod.o tracerid_mod.o tropopause_mod.o
setemis_adj.o: adj_arrays_mod.o aircraft_nox_mod.o biofuel_mod.o biomass_mod.o comode_mod.o dao_mod.o diag_mod.o drydep_mod.o edgar_mod.o emep_mod.o emissions_mod.o grid_mod.o icoads_ship_mod.o lightning_nox_mod.o logical_mod.o paranox_adj_mod.o paranox_mod.o pbl_mix_mod.o pressure_mod.o tracerid_mod.o tropopause_mod.o
sfcwindsqr.o: dao_mod.o
smvgear.o: comode_mod.o error_mod.o
soilnoxems.o: checkpt_mod.o dao_mod.o diag_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_adj_mod.o logical_mod.o time_mod.o
soiltype.o: time_mod.o
strat_chem_adj_mod.o: adj_arrays_mod.o bpch2_mod.o checkpoint_mod.o dao_mod.o error_mod.o linoz_adj_mod.o logical_adj_mod.o logical_mod.o strat_chem_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o
strat_chem_mod.o: adj_arrays_mod.o bpch2_mod.o checkpoint_mod.o dao_mod.o directory_mod.o error_mod.o grid_mod.o linoz_mod.o logical_adj_mod.o logical_mod.o netcdf_util_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o upbdflx_mod.o
streets_anthro_mod.o: bpch2_mod.o directory_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o regrid_a2a_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
sulfate_adj_mod.o: adj_arrays_mod.o bravo_mod.o cac_anthro_mod.o checkpt_mod.o comode_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o epa_nei_mod.o error_mod.o gfed2_biomass_mod.o global_hno3_mod.o global_no3_mod.o global_oh_mod.o grid_mod.o htap_mod.o logical_adj_mod.o logical_mod.o nei2005_anthro_mod.o nei2008_anthro_mod.o pbl_mix_mod.o pressure_mod.o seasalt_mod.o sulfate_mod.o time_mod.o tracer_mod.o tracerid_mod.o tropopause_mod.o wetscav_adj_mod.o wetscav_mod.o
sulfate_mod.o: adj_arrays_mod.o arctas_ship_emiss_mod.o biomass_mod.o bpch2_mod.o bravo_mod.o cac_anthro_mod.o checkpt_mod.o comode_mod.o dao_mod.o diag_mod.o directory_mod.o drydep_mod.o edgar_mod.o emep_mod.o epa_nei_mod.o error_mod.o file_mod.o future_emissions_mod.o gfed2_biomass_mod.o gfed3_biomass_mod.o global_hno3_mod.o global_no3_mod.o global_oh_mod.o grid_mod.o htap_mod.o icoads_ship_mod.o isoropiaII_adj_mod.o logical_adj_mod.o logical_mod.o m_netcdf_io_close.o m_netcdf_io_get_dimlen.o m_netcdf_io_open.o m_netcdf_io_read.o m_netcdf_io_readattr.o nei2005_anthro_mod.o nei2008_anthro_mod.o pbl_mix_mod.o pressure_mod.o rcp_mod.o regrid_1x1_mod.o regrid_a2a_mod.o scale_anthro_mod.o seasalt_mod.o streets_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o uvalbedo_mod.o wetscav_mod.o
tagged_co_adj_mod.o: adj_arrays_mod.o biofuel_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_pl_mod.o directory_mod.o error_mod.o global_nox_mod.o global_oh_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
tagged_co_mod.o: adj_arrays_mod.o biofuel_mod.o biomass_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_pl_mod.o directory_mod.o error_mod.o global_nox_mod.o global_oh_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pbl_mix_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
tagged_ox_adj_mod.o: adj_arrays_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_pl_mod.o directory_mod.o drydep_mod.o error_mod.o grid_mod.o logical_mod.o pbl_mix_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
tagged_ox_mod.o: adj_arrays_mod.o bpch2_mod.o dao_mod.o diag_mod.o diag_pl_mod.o directory_mod.o drydep_mod.o error_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pbl_mix_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
time_mod.o: charpak_mod.o error_mod.o grid_mod.o julday_mod.o
toms_mod.o: bpch2_mod.o directory_mod.o error_mod.o time_mod.o transfer_mod.o
tpcore_bc_mod.o: adj_arrays_mod.o bpch2_mod.o directory_mod.o error_mod.o file_mod.o grid_mod.o logical_mod.o time_mod.o tracer_mod.o
tpcore_mod.o: dao_mod.o diag_mod.o global_ch4_mod.o grid_mod.o pressure_mod.o time_mod.o tracer_mod.o
tpcore_window_mod.o: dao_mod.o diag_mod.o global_ch4_mod.o grid_mod.o pressure_mod.o time_mod.o tracer_mod.o
tracer_mod.o: error_mod.o
tracerid_mod.o: charpak_mod.o error_mod.o logical_mod.o tracer_mod.o
transfer_mod.o: error_mod.o
transport_mod.o: adj_arrays_mod.o dao_mod.o diag_mod.o error_mod.o grid_mod.o logical_adj_mod.o logical_mod.o pjc_pfix_geos5_window_mod.o pjc_pfix_geosfp_window_mod.o pjc_pfix_mod.o pressure_mod.o time_mod.o tpcore_bc_mod.o tpcore_fvdas_mod.o tpcore_geos5_window_mod.o tpcore_geosfp_window_mod.o tpcore_mod.o tpcore_window_mod.o tracer_mod.o
tropopause.o: dao_mod.o diag_mod.o logical_mod.o pressure_mod.o tropopause_mod.o
tropopause_mod.o: bpch2_mod.o comode_mod.o dao_mod.o directory_mod.o error_mod.o logical_mod.o pressure_mod.o transfer_mod.o
upbdflx_adj_mod.o: adj_arrays_mod.o bpch2_mod.o dao_mod.o directory_mod.o error_mod.o linoz_adj_mod.o logical_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
upbdflx_mod.o: bpch2_mod.o dao_mod.o directory_mod.o error_mod.o linoz_mod.o logical_mod.o pressure_mod.o tagged_ox_mod.o time_mod.o tracer_mod.o tracerid_mod.o transfer_mod.o tropopause_mod.o
uvalbedo_mod.o: bpch2_mod.o directory_mod.o error_mod.o transfer_mod.o
vistas_anthro_mod.o: bpch2_mod.o directory_mod.o epa_nei_mod.o error_mod.o future_emissions_mod.o grid_mod.o logical_mod.o regrid_1x1_mod.o scale_anthro_mod.o time_mod.o tracer_mod.o tracerid_mod.o
weak_constraint_mod.o: adj_arrays_mod.o bpch2_mod.o comode_mod.o directory_adj_mod.o error_mod.o file_mod.o gckpp_adj_Global.o grid_mod.o logical_adj_mod.o logical_mod.o restart_mod.o time_mod.o tracer_mod.o unix_cmds_mod.o
wetscav_adj_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o diag_mod.o error_mod.o grid_mod.o logical_adj_mod.o logical_mod.o ocean_mercury_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o wetscav_mod.o
wetscav_mod.o: adj_arrays_mod.o checkpt_mod.o dao_mod.o diag_mod.o error_mod.o logical_adj_mod.o logical_mod.o ocean_mercury_mod.o pressure_mod.o time_mod.o tracer_mod.o tracerid_mod.o
xltmmp.o: dao_mod.o
xtra_read_mod.o: bpch2_mod.o dao_mod.o diag_mod.o directory_mod.o error_mod.o file_mod.o logical_mod.o time_mod.o transfer_mod.o unix_cmds_mod.o

rdland.o: dao_mod.o logical_mod.o drydep_mod.o
