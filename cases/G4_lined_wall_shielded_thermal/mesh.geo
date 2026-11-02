// --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. ---
//
//  2D axisymmetric section of a shielded, lined, gamma-heated cylinder:
//  shield Rs..Rso, coolant channel (not meshed), liner Rw..Ri, vessel Ri..Ro.
//  Structured mesh, the field is radial. The shield is a separate body.
//
// --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. ---

// shield
Rs  = 0.260; // shield inner face (m)
Rso = 0.275; // shield outer face (m)

// liner+vessel
Rw  = 0.296; // wetted surface (m)
Ri  = 0.300; // vessel inner surface (m)
Ro  = 0.400; // vessel outer surface (m)
Lz  = 2.000; // height (m)

n_S = 31;    // nodes across the shield (0.5 mm cells)
n_L = 9;     // nodes across the liner (0.5 mm cells)
n_V = 101;   // nodes across the vessel (1 mm cells; 1/mu = 37 mm)
n_z = 41;    // nodes along z

// liner and vessel, as in G4_lined_wall_thermal
Point(1) = {Rw, 0, 0};
Point(2) = {Ri, 0, 0};
Point(3) = {Ro, 0, 0};
Point(4) = {Ro, Lz, 0};
Point(5) = {Ri, Lz, 0};
Point(6) = {Rw, Lz, 0};

Line(1) = {1, 2};  // bottom, liner
Line(2) = {2, 3};  // bottom, vessel
Line(3) = {3, 4};  // outer radius
Line(4) = {4, 5};  // top, vessel
Line(5) = {5, 6};  // top, liner
Line(6) = {6, 1};  // wetted surface
Line(7) = {2, 5};  // interface r = Ri

Curve Loop(1) = {1, 7, 5, 6};
Plane Surface(1) = {1};
Curve Loop(2) = {2, 3, 4, -7};
Plane Surface(2) = {2};

// the shield
Point(11) = {Rs,  0, 0};
Point(12) = {Rso, 0, 0};
Point(13) = {Rso, Lz, 0};
Point(14) = {Rs,  Lz, 0};

Line(11) = {11, 12}; // bottom, shield
Line(12) = {12, 13}; // shield outer face
Line(13) = {13, 14}; // top, shield
Line(14) = {14, 11}; // shield inner face

Curve Loop(3) = {11, 12, 13, 14};
Plane Surface(3) = {3};

Transfinite Line {1, 5} = n_L;
Transfinite Line {2, 4} = n_V;
Transfinite Line {11, 13} = n_S;
Transfinite Line {3, 6, 7, 12, 14} = n_z;
Transfinite Surface {1, 2, 3};
Recombine Surface {1, 2, 3};

Physical Surface("liner", 10) = {1};
Physical Surface("steel", 11) = {2};
Physical Surface("shield", 12) = {3};
Physical Curve("wetted_surface", 1) = {6};
Physical Curve("outer_radius", 2) = {3};
Physical Curve("bottom", 3) = {1, 2, 11};
Physical Curve("top", 4) = {4, 5, 13};
Physical Curve("shield_inner", 5) = {14};
Physical Curve("shield_outer", 6) = {12};
