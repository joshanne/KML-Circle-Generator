require './submodules/kml_polygon/lib/kml_polygon.rb'

puts KmlPolygon::kml_regular_polygon(ARGV[0].to_f, ARGV[1].to_f, ARGV[2].to_i, ARGV[3].to_i)