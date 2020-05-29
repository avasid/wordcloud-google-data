import pickle

import kivy
kivy.require("1.9.1")

from datetime import datetime
from datetime import timedelta

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import NumericProperty
from wordcloud import WordCloud, STOPWORDS


class DataHandler():

    def __init__(self):
        # File where the data is stored as dictionary(created by json2dict.py)
        with open("./data.pkl", 'rb') as fh:
            self.dataset = pickle.load(fh)

    def get_start_parameters(self):
        start_time = list(self.dataset.keys())[0][0]
        end_time = list(self.dataset.keys())[-1][0]
        return start_time, end_time

    def get_data(self, st, en):
        run = False
        data = ""
        print("Start interval:", st)
        print("End interval:", en)
        for k, v in self.dataset.items():
            datetime_k = k[0]
            if run is False:
                if datetime_k < st:
                    continue
                elif datetime_k >= st:
                    run = True
                    data += v + " "
            else:
                if datetime_k <= en:
                    data += v + " "
                else:
                    run = False
                    break
        return data

    def create_wc(self, st, en):
        cloud = WordCloud(background_color='white', width=1920, height=1080)
        print("Generating image")
        cloud.generate(self.get_data(st, en))
        cloud.to_file("./wordcloud.jpg")


class WidgetContainer(GridLayout, DataHandler):

    def __init__(self, **kwargs):

        # super function can be used to gain access
        # to inherited methods from a parent or sibling
        # class that has been overwritten in a class object.
        super(WidgetContainer, self).__init__(**kwargs)

        self.cols = 3
        self.rows = 3

        self.start_time, self.end_time = self.get_start_parameters()
        self.create_wc(self.start_time, self.end_time)
        self.diff = self.end_time - self.start_time

        self.locked = False

        # declaring the slider and adding some effects to it
        self.start_control = Slider(min=0, max=100, value=0, value_track=True, value_track_color=[
                                    0, 0, 1, 1], size_hint_y=None, height=30)
        self.end_control = Slider(min=0, max=100, value=100, value_track=True, value_track_color=[
                                  1, 0, 0, 1], size_hint_y=None, height=30)

        # 1st row
        self.add_widget(Label(text='', size_hint_x=None, width=100))
        self.image = AsyncImage(source="./wordcloud.jpg")
        self.add_widget(self.image)
        self.add_widget(Label(text='', size_hint_x=None, width=100))

        # 2nd row
        self.togglebutton = ToggleButton(
            text='unlocked', group='slider_lock', size_hint_x=None, width=100, size_hint_y=None, height=30)
        self.add_widget(self.togglebutton)
        self.add_widget(self.start_control)
        self.start_value = Label(text=datetime.strftime(
            self.start_time, '%Y-%m-%d'), size_hint_x=None, width=100, size_hint_y=None, height=30)
        self.add_widget(self.start_value)

        # 3rd row
        self.add_widget(Label(text='', size_hint_x=None,
                              width=100, size_hint_y=None, height=30))
        self.add_widget(self.end_control)
        self.end_value = Label(text=datetime.strftime(
            self.end_time, '%Y-%m-%d'), size_hint_x=None, width=100, size_hint_y=None, height=30)
        self.add_widget(self.end_value)

        # On the slider objects Attach a callback
        # for the attribute named "value_normalized"
        self.start_control.bind(value_normalized=self.on_value_start)
        self.end_control.bind(value_normalized=self.on_value_end)

        # Attach callback to attribute "state" of togglebutton
        self.togglebutton.bind(state=self.on_pressed)

    # Adding functionality behind the sliders and togglebutton
    # i.e when pressed increase the value
    def on_value_start(self, instance, value):
        print("Changing start point")
        self.start_control.value_normalized = min(
            self.start_control.value_normalized, self.end_control.value_normalized)
        value = self.start_control.value_normalized
        self.start_value.text = datetime.strftime(
            self.start_time + self.start_control.value_normalized * self.diff, '%Y-%m-%d')
        if self.locked == True:
            print("Changing end point")
            self.end_control.value_normalized = min(
                1, self.start_control.value_normalized + self.locked_diff)
        self.create_wc(self.start_time + self.start_control.value_normalized *
                       self.diff, self.start_time + self.end_control.value_normalized * self.diff)
        print("Reading image")
        self.image.reload()

    def on_value_end(self, instance, value):
        print("Changing end point")
        self.end_control.value_normalized = max(
            self.end_control.value_normalized, self.start_control.value_normalized)
        value = self.end_control.value_normalized
        self.end_value.text = datetime.strftime(
            self.start_time + self.end_control.value_normalized * self.diff, '%Y-%m-%d')
        if self.locked == True:
            print("Changing start point")
            self.start_control.value_normalized = max(
                0, self.end_control.value_normalized - self.locked_diff)
        self.create_wc(self.start_time + self.start_control.value_normalized * self.diff,
                       self.start_time + (self.end_control.value_normalized * self.diff))
        print("Reading image")
        self.image.reload()

    def on_pressed(self, instance, state):
        if state == 'down':
            self.togglebutton.text = "locked"
            self.locked_diff = self.end_control.value_normalized - \
                self.start_control.value_normalized
            self.locked = True
        else:
            self.togglebutton.text = "unlocked"
            self.locked_diff = None
            self.locked = False

# The app class


class SliderExample(App):

    def build(self):
        widgetContainer = WidgetContainer()
        return widgetContainer


# creating the object root for ButtonApp() class
root = SliderExample()

# run function runs the whole program
# i.e run() method which calls the
# target function passed to the constructor.
root.run()
