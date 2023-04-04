const { execSync } = require("child_process");
const config = require('./config')

/*
 ************* Non modifiable code below *************
 */

const placemark_list = config.radius_list.reverse().map((radius, index) => {
    const output = execSync(
      `ruby generate_circle_kml.rb ${config.location.longitude} ${config.location.latitude} ${radius} ${config.vertices}`
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

const style_list = config.style_colors.reverse().map((color_table, index) => {
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
    <name>${config.location.name}</name>
    <description/>
${style_list}
    <Folder>
      <name>${config.folder_name}</name>
${placemark_list}
    </Folder>
  </Document>
</kml>
`;

console.log(kmlOutput);
