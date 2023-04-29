from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField, validators
import os
from wtforms.validators import NumberRange
import main_functions
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def get_key(filename, api_name):
    api_key_dict = main_functions.read_from_file(filename)
    my_api_key = api_key_dict[api_name]
    return my_api_key


nasa_api_key = get_key("api_keys.json", "nasa_key")


# This function receives the name of a camera as a string, a day in Mars as integer, and the api_key for the NASA api
# as a string
def get_list_NASA_pictures(camera_name, sol, api_key):
    print(camera_name)
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol}&api_key={api_key}"
    mars_pics = requests.get(url).json()
    main_functions.save_to_file(mars_pics, "mars_pics.json")
    mars_pics = main_functions.read_from_file("mars_pics.json")
    lst = []
    for i in mars_pics["photos"]:
        if i["camera"]["name"] == camera_name:
            lst.append(i["img_src"])
    return lst


class Mars_camera(FlaskForm):
    camera = SelectField("Choose a camera", [validators.DataRequired()],
                         choices=[
                             ("FHAZ", "Front Hazard Avoidance Camera"),
                             ("RHAZ", "Rear Hazard Avoidance Camera"),
                             ("MAST", "Mast Camera"),
                             ("CHEMCAM", "Chemistry and Camera Complex"),
                             ("MAHLI", "Mars Hand Lens Imager"),
                             ("MARDI", "Mars Descent Imager"),
                             ("NAVCAM", "Navigation Camera")])
    sol = IntegerField("Sol", validators=[
        NumberRange(min=1, max=1000, message='Invalid length')])  # Sol is Martian rotation or day
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = Mars_camera()
    if form.validate_on_submit():
        camera_entered = form.camera.data
        sol_entered = form.sol.data
        list_of_images = get_list_NASA_pictures(camera_entered, sol_entered, nasa_api_key)
        return render_template("mars_pictures.html", list_of_images=list_of_images, length=len(list_of_images))
    return render_template('mars.html', form=form)


if __name__ == '__main__':
    app.run(port=7070)