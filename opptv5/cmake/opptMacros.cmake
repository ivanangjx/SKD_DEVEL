MACRO(SUBDIRLIST result curdir)
  FILE(GLOB children RELATIVE ${curdir} ${curdir}/*)
  SET(dirlist "")
  FOREACH(child ${children})
    IF(IS_DIRECTORY ${curdir}/${child})
      LIST(APPEND dirlist ${child})
    ENDIF()
  ENDFOREACH()
  SET(${result} ${dirlist})
ENDMACRO()

macro(ADD_TRANSITION_PLUGIN name src)
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})   
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES})    
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)   
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/transitionPlugins)
endmacro()

macro(ADD_OBSERVATION_PLUGIN name src)
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES}) 
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/observationPlugins)
endmacro()

macro(ADD_INITIAL_BELIEF_PLUGIN name src)
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})   
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES})   
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/initialBeliefPlugins)
endmacro()

macro(ADD_TERMINAL_PLUGIN name src)
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES})
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/terminalPlugins)
endmacro()

macro(ADD_HEURISTIC_PLUGIN name src)   
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES})
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/heuristicPlugins)
endmacro()

macro(ADD_REWARD_PLUGIN name src)   
   set(TARGET_LINK_LIBRARIES ${ARGN})   
   add_library(${name} SHARED ${src})
   target_link_libraries(${name} ${TARGET_LINK_LIBRARIES})
   target_include_directories(${name} PUBLIC $<INSTALL_INTERFACE:include>;${oppt_INCLUDE_TARGETS};${oppt_INCLUDE_DIRS})
   set_target_properties(${name} PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED YES)
   install(TARGETS ${name} LIBRARY DESTINATION ${CMAKE_INSTALL_DATADIR}/oppt/plugins/rewardPlugins)
endmacro()
