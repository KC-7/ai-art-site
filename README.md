# AI Art Site

Live Link: https://ai-art-site.herokuapp.com/

---

## Agile 

### Phase 1 - MVP - Art Gallery

#### Sprint 1

- Create & Manage Posts 
- Moderate Posts 
- Private Posts

#### Sprint 2 

- Site Pagination 
- View Likes
- View Posts / Images

#### Sprint 3

- View Comments
- Open Images

#### Sprint 4

- Account Registration
- Login
- Logout

#### Sprint 5 

- Commenting

#### Sprint 6

- Like Posts
- Update default logout and sign up templates (missed in sprint 4)

---

### Phase 2 - AI Art Creation

#### Sprint 7 

- XXX

---


## Bugs: 

### HTML code being displayed on the post previews

I used striptages filter to remove the code tags before truncating it (restricting the amount of words that are displayed on image preview):

    <p class="card-text">
        {{ post.description|striptags|truncatewords:20 }}
    </p>

---

## Documentation: 

### django Pagination 

Link: https://docs.djangoproject.com/en/4.2/topics/pagination/

The above documentation shows hows to use the pagination class. The project was modifed to only display the last button if there is more that one extra page. The reverese was done for the last page. The next and prev page button will only display if there is a page to go to. 

### Code Institute django blog walkthrough project

Link: #

This project was used for inspiration for the project. I followed Code Institutes guide for Django projects (xxxxxxxxxxx) as to avoid issues with creation and deployment.

### Dall-E Image Generation 

Introduction to API Link: https://platform.openai.com/docs/guides/images/introduction

Image Generation Link: https://platform.openai.com/docs/guides/images/usage

### django Slugify

Link: https://www.fullstackpython.com/django-utils-text-slugify-examples.html

Link: https://docs.djangoproject.com/en/4.2/ref/utils/


    Example: 

        from django.utils.text import format_lazy
    from django.utils.translation import pgettext_lazy

    urlpatterns = [
        path(
            format_lazy("{person}/<int:pk>/", person=pgettext_lazy("URL", "person")),
            PersonDetailView.as_view(),
        ),
    ]

    >>> slugify(" Joel is a slug ")
    'joel-is-a-slug'


### Disable Right Click on Images

Link: https://www.dotnettricks.com/learn/aspnet/disable-right-click-on-web-page-and-images

Right clicking on images was disabled by using """ oncontextmenu='return false;' """

### Allow only registed users to Download Images 

Link: https://docs.djangoproject.com/en/4.2/ref/templates/builtins/

A simple if statment was implemented. 

Example from Django Docs: 

    {% if athlete_list %}
        Number of athletes: {{ athlete_list|length }}
    {% elif athlete_in_locker_room_list %}
        Athletes should be out of the locker room soon!
    {% else %}
        No athletes.
    {% endif %}

### Aesthicaly pleasing icons

Link: https://fontawesome.com/search?q=next&o=r&m=free

I used free icons from FontAwesome. 

### Loading Wheel for AI Art Generation & Wait Time Updates

Link: https://loading.io/

The loading wheel / spinner was created using the Loading.io for free. The chosen option allowed me to use the website colour palette to create a custom spinner. 

Link: https://www.washington.edu/accesscomputing/webd2/student/unit5/module2/lesson5.html

Javascript is used to hide and display the appropiates elements, ie. once the button is pressed, it is removed, a loading wheel appears and text, after 3 seconds, the text is updated and again after 30 seconds. This is similar to how the quiz features where implement in my JS Car Quiz Project - XXXXXXXXXXXXXXXXXXXXXXXXX

### Upload Form 



### Auto Upload AI Generation to Website


### Keep footer at base of page

Details: XXXXXXXXXXXXXXXXX

JS was implemented to keep the footer at the base on the content. This was implemented as the footer size is not fixed, it changes based on the screen size and current content.

### CSS Variables for Colour Palette

Link: https://www.w3schools.com/css/css3_variables.asp

I wanted to experiment with using different colour palettes on the site to improve the appearance of the site. Instead of assigning different colours to each class, i created a base colour pallet at the top of the css file, once the variables were assigned to their appropiate classes, i was able to change entire colour palettes quickly and easily. It also makes it easier to select suitable colour group when writing the code as the 8 colour options pop up on my ide once the first part of the var is enetered. 

    Example: 
        :root {
        --blue: #1e90ff;
        --white: #ffffff;
        }

        body { background-color: var(--blue); }


### Text Logo

Link: https://www.w3schools.com/css/css3_3dtransforms.asp

The text based logo was created to look playful, to achieve this I experimented with css such as transform to to rotate the letters. 


### Pillow Image

Link: https://pillow.readthedocs.io/en/stable/reference/Image.html


### BytesIO 

Link: https://docs.python.org/3/library/io.html


### Adding Messages with Django

Link: https://docs.djangoproject.com/en/4.2/ref/contrib/messages/

Link2: https://django-messages.readthedocs.io/en/latest/



---

## To Be Implemented: 

### Moderation: 

Link: https://platform.openai.com/docs/guides/moderation/overview

Alt Moderation TBA - XXXX (one that can cross check user input against a list)

