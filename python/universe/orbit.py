from polycircles import polycircles
import simplekml

def add_circle(latitude, longitude, radius, color='ff0000ff', name="KML Circle", description="", filled=False):
    """
    Generates a KML circle.

    Args:
        latitude (float): Latitude of the circle's center.
        longitude (float): Longitude of the circle's center.
        radius (float): Radius of the circle in meters.
        color (str, optional): Color of the circle outline in AABBGGRR format. Defaults to 'ff0000ff' (blue).
        name (str, optional): Name of the circle in the KML file. Defaults to "KML Circle".
        description (str, optional): Description of the circle in the KML file. Defaults to "".
        filled (bool, optional): Whether to fill the circle. Defaults to False.

    Returns:
        str: KML representation of the circle.
    """

    # Create a Kml object
    kml = simplekml.Kml()

    # Create a Polycircle object
    pc = polycircles.Polycircle(latitude=latitude, longitude=longitude, radius=radius, number_of_vertices=36)

    # Create a new polygon in the KML
    pol = kml.newpolygon(name=name, description=description, outerboundaryis=pc.to_kml())

    # Set the style
    pol.style.linestyle.color = simplekml.Color.hex(color)
    pol.style.linestyle.width = 2
    pol.style.polystyle.fill = 1 if filled else 0

    # Return the KML as a string
    return kml.kml(format=True)

if __name__ == '__main__':
    # Example usage
    latitude = 34.0522  # Example latitude (Los Angeles)
    longitude = -118.2437 # Example longitude (Los Angeles)
    radius = 1000       # Example radius in meters

    kml_string = add_circle(latitude, longitude, radius, color='ff0000ff', name="Los Angeles Circle", description="Circle around Los Angeles")
    print(kml_string)

    # You can save the KML string to a file:
    # with open("circle.kml", "w") as f:
    #     f.write(kml_string)
