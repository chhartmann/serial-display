//-----------------------------------------------------------------------
// Yet Another Parameterized Projectbox generator
//
//  This is a box for the serial display
//-----------------------------------------------------------------------

include <../YAPPgenerator_v3.scad>

//-- which part(s) do you want to print?
printBaseShell        = true;
printLidShell         = true;
printSwitchExtenders  = false;
shiftLid              = 10;  // Set the distance between the lid and base when rendered or previewed side by side
                            
//-- padding between pcb and inside wall
paddingFront        = 1;
paddingBack         = 1;
paddingRight        = 1;
paddingLeft         = 1;

// ********************************************************************
// The Following will be used as the first element in the pbc array

//Defined here so you can define the "Main" PCB using these if wanted
pcbLength           = 58.0; // Front to back
pcbWidth            = 36.0; // Side to side
pcbThickness        = 1.2;
standoffHeight      = 1.0;  //-- How much the PCB needs to be raised from the base to leave room for solderings 
standoffDiameter    = 7;
standoffPinDiameter = 2.4;
standoffHoleSlack   = 0.4;

wallThickness       = 1.8;
basePlaneThickness  = 1.2;
lidPlaneThickness   = 1.2;

//-- Total height of box = lidPlaneThickness 
//                       + lidWallHeight 
//--                     + baseWallHeight 
//                       + basePlaneThickness
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
baseWallHeight      = 7;
lidWallHeight       = 5;

//-- ridge where base and lid off box can overlap
//-- Make sure this isn't less than lidWallHeight
ridgeHeight         = 5.0;
ridgeSlack          = 0.3;
roundRadius         = 2.0;

//---------------------------
//--     C O N T R O L     --
//---------------------------
// -- Render --
renderQuality             = 8;          //-> from 1 to 32, Default = 8

// --Preview --
previewQuality            = 5;          //-> from 1 to 32, Default = 5
showSideBySide            = true;       //-> Default = true
onLidGap                  = 0;  // tip don't override to animate the lid opening
//onLidGap                  = ((ridgeHeight) - (ridgeHeight * abs(($t-0.5)*2)))*2;  // tip don't override to animate the lid opening/closing
colorLid                  = "YellowGreen";   
alphaLid                  = 1;
colorBase                 = "BurlyWood";
alphaBase                 = 1;
hideLidWalls              = false;      //-> Remove the walls from the lid : only if preview and showSideBySide=true 
hideBaseWalls             = false;      //-> Remove the walls from the base : only if preview and showSideBySide=true  
showOrientation           = true;       //-> Show the Front/Back/Left/Right labels : only in preview
showPCB                   = false;      //-> Show the PCB in red : only in preview 
showSwitches              = false;      //-> Show the switches (for pushbuttons) : only in preview 
showButtonsDepressed      = false;      //-> Should the buttons in the Lid On view be in the pressed position
showOriginCoordBox        = false;      //-> Shows red bars representing the origin for yappCoordBox : only in preview 
showOriginCoordBoxInside  = false;      //-> Shows blue bars representing the origin for yappCoordBoxInside : only in preview 
showOriginCoordPCB        = false;      //-> Shows blue bars representing the origin for yappCoordBoxInside : only in preview 
showMarkersPCB            = false;      //-> Shows black bars corners of the PCB : only in preview 
showMarkersCenter         = true;      //-> Shows magenta bars along the centers of all faces  
inspectX                  = 0;          //-> 0=none (>0 from Back)
inspectY                  = 0;          //-> 0=none (>0 from Right)
inspectZ                  = 0;          //-> 0=none (>0 from Bottom)
inspectXfromBack          = true;       //-> View from the inspection cut foreward
inspectYfromLeft          = true;       //-> View from the inspection cut to the right
inspectZfromBottom        = true;       //-> View from the inspection cut up
//---------------------------
//--     C O N T R O L     --
//---------------------------


displayMounts =
[
  
  [ // This is for a SSD-1306 OLED Display v1.1 with vcc-gnd-scl-sda Pinout
    32, //xPos
    20, // yPos
    56.0, // displayWidth
    34.0, //displayHeight
    1.5, //pinInsetH
    1.0, //pinInsetV
    2, //pinDiameter
    0, //postOverhang
    2.4-lidPlaneThickness, //walltoPCBGap
    0, //pcbThickness
    44.5, //windowWidth
    35.0, //windowHeight
    0, //windowOffsetH
    0, //windowOffsetV
    false, //bevel
    0, // rotation
    yappDefault,//snapDiameter
    yappDefault,
    yappCenter,  
  ]
];

cutoutsBase  = 
[
   [125, 70,  6, -4, 8, yappCircleWithKey, undef, 0, yappCenter], // External key of height 4
   [125, 50,  6,  0, 8, yappCircleWithKey, undef, 0, yappCenter], // a depth of Zero just creates the flat for a key
   [125, 30,  6,  4, 8, yappCircleWithKey, undef, 0, yappCenter], // Key with depth of 4
];


//---- This is where the magic happens ----
cutoutsFront = 
[
   [pcbWidth/2 - 10/2, 0, 10, 4, 5, yappRectangle],
];  

cutoutsLeft = 
[
   [pcbLength/2, 3, 0, 10, 1.5, yappCircle, yappCenter],
];  

pcbStands = [
  [45, 5, yappBaseOnly]
];



YAPPgenerate();

