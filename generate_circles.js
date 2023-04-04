const { execSync } = require("child_process");

// Configurable options

const location_name = "Null Island";
const folder_name = "Rings";
const latitude = 0;
const longitude = 0;
const vertices = 50;
const radius_list = [20,40,60,80,100,150,200];
const style_colors = [
  [0xff1400FF, 0x4d1400FF], // Red
  [0xff1478FF, 0x4d1478FF], // Orange
  [0xff14F0FF, 0x4d14F0FF], // Yellow
  [0xff008C14, 0x4d008C14], // Green
  [0xff780A78, 0x4d780A78], // Indigo
  [0xffF00014, 0x4dF00014], // Blue
  [0xffff008f, 0x4fff008f]  // Violet
];


/*
 ************* Non modifiable code below *************
 */

const placemark_list = radius_list.reverse().map((radius, index) => {
    const output = execSync(
      `ruby generate_circle_kml.rb ${longitude} ${latitude} ${radius} ${vertices}`
    ).toString();

    const placemark = 
`
      <Placemark>
        <name>${radius}m</name>
        <styleUrl>#polygon-${index}</styleUrl>
${output}
      </Placemark>`;
    return placemark;
  }).join("\n");

const style_list = style_colors.reverse().map((color_table, index) => {
  const style =
`
    <Style id="polygon-${index}-normal">
      <LineStyle>
        <color>${color_table[0].toString(16)}</color>
        <width>2</width>
      </LineStyle>
      <PolyStyle>
        <color>${color_table[1].toString(16)}</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    <Style id="polygon-${index}-highlight">
      <LineStyle>
        <color>${color_table[0].toString(16)}</color>
        <width>2.8</width>
      </LineStyle>
      <PolyStyle>
        <color>${color_table[1].toString(16)}</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    <StyleMap id="polygon-${index}">
      <Pair>
        <key>normal</key>
        <styleUrl>#polygon-${index}-normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#polygon-${index}-highlight</styleUrl>
      </Pair>
    </StyleMap>`;
    return style;
}).join("\n");



const kmlOutput = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>${location_name}</name>
    <description/>
${style_list}
    <Folder>
      <name>${folder_name}</name>
${placemark_list}
    </Folder>
  </Document>
</kml>
`;

console.log(kmlOutput);
