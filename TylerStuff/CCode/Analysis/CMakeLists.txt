art_make(  MODULE_LIBRARIES  larpandora::LArPandoraInterface
                             lardata::RecoObjects  
                             lardataobj::RecoBase
                             lardataobj::AnalysisBase
                             larreco::RecoAlg

                             art::Framework_Core
                             art::Framework_Principal
                             art::Framework_Services_Registry
                             art_root_io::tfile_support
                             art_root_io::TFileService_service
                             art::Persistency_Common
                             art::Persistency_Provenance
                             art::Utilities
                             larsim::MCCheater_ParticleInventoryService_service
                             larsim::Utils 

                             cetlib::cetlib
                             cetlib_except::cetlib_except
                             ${LARRECO_LIB}
                             ${LARDATA_LIB}
                             ${ART_FRAMEWORK_SERVICES_BASIC}
                             ${ART_FRAMEWORK_SERVICES_OPTIONAL}
                             ${MF_UTILITIES}
                             ${FHICLCPP}
                             ${CLHEP}

                             messagefacility::MF_MessageLogger
                             fhiclcpp::fhiclcpp
                             ROOT::Geom
                             ROOT::XMLIO
                             ROOT::Gdml
                             ROOT::Core

                             ${ROOT_BASIC_LIB_LIST}
                             ${ROOT_SPECTRUM}
                             ${ROOT_ROOFIT}
                             ${ROOT_ROOFITCORE}
        )
install_fhicl()
install_source()
