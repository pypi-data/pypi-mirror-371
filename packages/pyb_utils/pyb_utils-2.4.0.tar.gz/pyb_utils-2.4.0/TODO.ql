= pyb_utils todo =

== v3.0 ==
* fix typo `localInerialPos` in named tuples
  - probably read through all the other field names to make sure they are
    spelled correctly
* remove deprecated GhostSphere

== v2.2.0 ==
~ add `rot{2,x,y,z}` functions; use scipy backend for rotations
~ add FrameRecorder
~ GhostObject.box (contributed) and add `client_id` parameter to GhostObject

== v2.1.0 ==
~ add contact force utilities
~ add tests for BulletBody offset inertial frame
~ add quatx{x,y,z} functions
~ rewrite based on UnitQuaterion class

== v2.0 ==
~ collision detection API refactor
~ robot enhancements and breaking changes

== v1.3.0 ==
~ add locked/actuated joints as in mm_central?
  - this would allow me to totally replace the mm_central implementation!
  - add pendulum and robot control examples

== v1.1.0 ==
~ add docs, hosted on readthedocs.io

== v1.0 ==
~ drop Python 3.7 support
~ add Python 3.11 support
~ bug fixes to camera, ghost example
~ change point cloud dimensions
~ change collision detector API such that robot and q are not required
~ getJointInfo for the named tuples
  - needs to be added to example and tests
~ add tests
  ~ bodies
  ~ camera
  ~ named tuples
  ~ collision
~ tox for automated testing

== other ==
* add type hints
* support spherical joints
