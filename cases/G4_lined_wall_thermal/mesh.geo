// --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. ---
//
//  2D axisymmetric section of a lined, gamma-heated cylinder: liner Ri..Rm,
//  vessel Rm..Ro. Structured mesh, the field is radial. The interface is a mesh
//  line, so each cell belongs to one material.
//
// --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. --- --.. ..- .-.. .-.. ---

Ri = 0.296;  // wetted surface (m)
Rm = 0.300;  // vessel inner surface (m)
Ro = 0.400;  // vessel outer surface (m)
Lz = 2.000;  // height (m)

n_L = 9;     // nodes across the liner (0.5 mm cells)
n_V = 101;   // nodes across the vessel (1 mm cells; 1/mu = 37 mm)
n_z = 41;    // nodes along z

Point(1) = {Ri, 0, 0};
Point(2) = {Rm, 0, 0};
Point(3) = {Ro, 0, 0};
Point(4) = {Ro, Lz, 0};
Point(5) = {Rm, Lz, 0};
Point(6) = {Ri, Lz, 0};

Line(1) = {1, 2};  // bottom, liner
Line(2) = {2, 3};  // bottom, vessel
Line(3) = {3, 4};  // outer radius
Line(4) = {4, 5};  // top, vessel
Line(5) = {5, 6};  // top, liner
Line(6) = {6, 1};  // inner radius (wetted surface)
Line(7) = {2, 5};  // interface r = Rm

Curve Loop(1) = {1, 7, 5, 6};
Plane Surface(1) = {1};
Curve Loop(2) = {2, 3, 4, -7};
Plane Surface(2) = {2};

Transfinite Line {1, 5} = n_L;
Transfinite Line {2, 4} = n_V;
Transfinite Line {3, 6, 7} = n_z;
Transfinite Surface {1, 2};
Recombine Surface {1, 2};

Physical Surface("liner", 10) = {1};
Physical Surface("steel", 11) = {2};
Physical Curve("inner_radius", 1) = {6};
Physical Curve("outer_radius", 2) = {3};
Physical Curve("bottom", 3) = {1, 2};
Physical Curve("top", 4) = {4, 5};
