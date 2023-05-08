# Cre8AI.art
Live Link: https://ai-art-site.herokuapp.com/

Custom Domain Link: Cre8AI.art

This web application allows users to create custom AI generated artwork using the impressive DALLE-2 API by OpenAI. The generated image is automatically shared as a public post. The user can view it, change it to private, edit the description, download the image or delete the post. User accounts are limited to 5 generations per day. Users can also use the upload form to share a generation from a different site (example, stable diffusion). The site also has an About section which is managed from the sites admin panel, this allows admins to alter and create additional pages as required. 

---

## Features

- User registration and authentication

- Image generation based on the user's text prompts

- Image upload and management

- User profile with bio and profile picture

- Post liking and commenting

- Public and private post visibility options

- Search and sort functionality

- Static pages for additional content

- Admin panel for managing posts, comments, user profiles, and static pages

---

## Technologies Used

- Django

- Python

- HTML

- CSS

- Javascript

- Cloudinary

- ElephantSQL

- OpenAI API

---

## Coding Overview

### URLs

The following URLs are used in the project:

| URL                         | Description                                        |
| ---                         | ---                                                |
| /                           | Home page, displays list of image posts            |
| /accounts/signup/           | User registration page                             |
| /upload/                    | Form for uploading new image posts                 |
| /generate_art/              | Form for generating art from text                  |
| /search/                    | Search page for image posts                        |
| /about/                     | About page, displays list of static pages          |
| /<slug:slug>/               | Detail page for a specific image post              |
| /like/<slug:slug>/          | Endpoint for liking/unliking a post                |
| /private/<slug:slug>/       | Endpoint for making a post private                 |
| /public/<slug:slug>/        | Endpoint for making a private post public again    |
| /delete/<slug:slug>/        | Endpoint for deleting a post                       |
| /profile/<str:username>/    | User profile page                                  |
| /post_edit/<slug:slug>/     | Form for editing a posted image's description      |
| /about/<slug:slug>/         | Detail page for a specific static page             |

### Models

- **Post**: A model for image posts, which includes fields for the image, title, slug, creator, timestamps, description, status (private/public), likes, and approval status.

- **Comment**: A model for comments on image posts, which includes fields for the associated post, name, email, body, timestamp, and approval status.

- **Profile**: A model for user profiles, which includes fields for the associated user, bio, profile picture, last generation timestamp, and generation count.

- **StaticPage**: A model for admin-created static pages, which includes fields for the title, slug, content, and status (private/public).

### Views

- **RegisterUser**: Handles user registration and creates a profile for the registered user.

- **PostList**: Displays a list of image posts, allows pagination, and supports sorting by most likes or most recent.

- **PostDetail**: Displays the details of an image post and supports adding comments.

- **PostLike**: Handles liking and unliking posts.

- **UploadForm**: Manages the form for uploading image posts.

- **GenerateArt**: Handles art generation requests and creates a public post with the generated art.

- **PostPrivate**: Handles making and viewing private posts.

- **PostPublic**: Allows users to make private posts public again.

- **DeletePost**: Handles the deletion of posts.

- **UserProfile**: Displays user profiles and allows editing of user bios and profile pictures.

- **Search**: Handles user image search functionality.

- **EditPost**: Handles editing post details.

- **StaticPageView**: Handles static pages that can be uploaded and updated by site admins.

- **AboutView**: Handles the about page and displays all of the admins' static pages.

### Forms

- **CommentForm**: A form for adding comments to posts.

- **PostForm**: A form for creating image posts, including a slug auto-generated from the title.

- **GenerateForm**: A form for text-to-image art generation, with a prompt field.

- **ProfileForm**: A form for editing user profiles, including bio and profile picture.

- **EditPostForm**: A form for editing posted images' descriptions.

### Utilities

- **generate_image_from_text(prompt)**: A function that generates an image from a text prompt using OpenAI's API. Takes a string 'prompt' as an argument and returns the URL of the generated image. Raises a ValueError if the API request is not successful.

### Admin

- **PostAdmin**: Admin configuration for the image posts, including list display, search fields, prepopulated fields, list filters, and custom actions such as making posts private and liking posts.

- **CommentAdmin**: Admin configuration for the comments on the posts, including list display, list filters, and search fields.

- **ProfileAdmin**: Admin configuration for the users' profiles, including list display, search fields, and custom actions such as resetting profile pictures and resetting daily generation count.

- **StaticPageAdmin**: Admin configuration for the static pages displayed in the About section, including list display, search fields, prepopulated fields, and custom actions such as making static pages private.

---

## Local Set Up Guide

- Clone the repository.

- Set up a virtual environment and install the required dependencies.

- Set up cloudinary and openai account.

- Create a .env file with the required environment variables:
    - "DATABASE_URL"
    - "SECRET_KEY"
    - "CLOUDINARY_URL"
    - "OPENAI_API_KEY"

- Apply database migrations and create a superuser account.

- Run the Django development server.

---

## Agile Sprint List

### Sprint 1
- Create & Moderate Posts
- Moderate Posts
- Private Posts

### Sprint 2
- Site Pagination
- View Posts
- View Likes
- View Comments

### Sprint 3
- Open Images
- Register Account
- Login
- Log out

### Sprint 4
- Comment on posts
- Like Posts
- User Uploads
- Upload Redirection

### Sprint 5
- AI Art Generation
- Image Downloads
- Total Number of Pages

### Sprint 6
- Search Images
- Filter Posted Images
- Account Page

### Sprint 7
- Update & Delete Posts + Make Private

#### ADITIONAL TO BE UPDATED ABOVE: 
- Image generation limit
- Disable image downloads for unregistered users
- Admin portal features

---

## Bugs

### Resolved Bugs

| Bug | Fix |
| --- | --- |
| HTML code being displayed on the post previews | I used the striptags filter to remove the code tags before truncating it (restricting the amount of words that are displayed on image preview) |
| Site went down and stopped working after deployment | After investigating, it turned out the issue was caused by a blank post that did not have a slug, despite numerous tests, I was unable to recreate another Post without a Slug or Title. I rectified the issue by adding a filter to the index template to remove posts without slugs from being displayed which allowed the site to load but it showed an empty post on the index page, I then deleted the empty post via the admin panel. I carried out numerous tests to recreate the issue but was unable to. If an empty post was somehow raised again, it would not cause the same issue. |

### Outstanding Bugs

| Bug | Comments |
| --- | --- |
| When the user generates an image with the same prompt as an image generated prior to May, it may dispay the previous generated image on the users post instead of the newly generated images | This issue arose after I made adjustments to the Cloudinary Public Image IDs, this issue does not occur with duplicated generations where the orginal was created in May or after. |
| Unable to access via the custom namecheap domain | Still testing and trying to resolve.................. |

---

## Testing

### Manual Testing

#### User Expectation Testing

| Test Case                                                  | Expected Result                                                                                     | Result |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|--------|
| Load the homepage                                          | Displays a list of posts with pagination and allows sorting by most likes or most recent            | ✅    |
| Register a new user                                        | Creates a user profile, logs in the user, and redirects to the homepage                             | ✅    |
| Log in an existing user                                    | Logs in the user and redirects to the homepage                                                      | ✅    |
| Upload a new post                                          | Displays the uploaded post in detail                                                                | ✅    |
| Generate AI art                                            | Generates AI art based on a given prompt and displays the resulting post in detail                  | ✅    |
| Search for posts                                           | Displays a list of posts that match the search query, paginates and gives option to filter by       | ✅    |
| View a user's profile                                      | Displays the user's profile with their posts and allows editing of bio and profile picture          | ✅    |
| Edit a post                                                | Displays the updated post in detail                                                                 | ✅    |
| Like/unlike a post                                         | Updates the post's like count                                                                       | ✅    |
| Make a post private                                        | Redirects to the private post's detail view and removes the post from the public listing            | ✅    |
| Make a post public                                         | Redirects to the public post's detail view and adds the post to the public listing                  | ✅    |
| Delete a post                                              | Removes the post and redirects to the user's profile                                                | ✅    |
| View the about page                                        | Displays the about page with a list of admin-created static pages                                   | ✅    |
| View a static page                                         | Displays the content of the static page                                                             | ✅    |

#### Functionality/Input-Validation

| Test Case                                                  | Expected Result                                                                                     | Result |
|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|--------|
| Register a new user with invalid input                     | Displays an error message and does not create a user profile                                        | ✅    |
| Log in with invalid credentials                            | Displays an error message and does not log in the user                                              | ✅    |
| Upload a post without required  input                      | Displays an error message and does not create the post                                              | ✅    |
| Generate AI art with invalid input                         | Displays an error message and does not generate the art                                             | ✅    |
| Generate more than the limit for AI art                    | Displays an error message and does not generate the art                                             | ✅    |
| Empty comment on a post                                    | Displays an error message and does not create the comment                                           | ✅    |
| Edit a post with empty input                               | Displays an error message and does not update the post                                              | ✅    |
| Update user profile with empty input                       | Displays an error message and does not update the user's profile                                    | ✅    |

---

## Deployment

TBC

---

## Future Development

I would have liked to implement some of the below features but was unable to due to timing restraints, these can be planned for development at a later stage:

- Set up additional sign up information as a requirement, such as email address, etc. 

- Set up password resets for user

- Set up print on demand products below each of the posts and payment processing for same

- Set up user private messaging system

- Set up comments section on user profiles

- Set up pagination on user profiles

- Set up a "Following" section and allow users to follow other creators

- Set up social sign up and login

- Set up a social share feature that allows users to share their generations easily on social media

- Set up automatic likes for users own posts

- Set up advertising on the site to generate revenue

- Set up subscription tiers: Free, Paid Plan and Supreme Plan. Restrict daily generations based on tier and amount of adverts displayed etc.

- Set up additional site analytics on the admin panel

---

## Useful Links & Documentation

| Link | Description |
| ---- | ----------- |
| [Django documentation](https://docs.djangoproject.com/en/3.2/) | Official Django documentation |
| [Django views](https://docs.djangoproject.com/en/3.2/topics/class-based-views/) | Class-based views in Django |
| [Django generic views](https://docs.djangoproject.com/en/3.2/ref/class-based-views/generic-display/) | Generic class-based views in Django |
| [Django forms](https://docs.djangoproject.com/en/3.2/topics/forms/) | Working with forms in Django |
| [Django model forms](https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/) | Creating forms from models in Django |
| [Django messages](https://docs.djangoproject.com/en/3.2/ref/contrib/messages/) | Django messages framework for displaying messages |
| [Django authentication](https://docs.djangoproject.com/en/3.2/topics/auth/) | Authentication in Django |
| [Django signals](https://docs.djangoproject.com/en/3.2/topics/signals/) | Signals in Django for decoupled applications |
| [Django queries](https://docs.djangoproject.com/en/3.2/topics/db/queries/) | Querying the database in Django |
| [Django Q objects](https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects) | Using Q objects in Django for complex lookups |
| [Django pagination](https://docs.djangoproject.com/en/3.2/topics/pagination/) | Pagination in Django |
| [Django decorators](https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#decorating-the-class) | Decorators in Django for class-based views |
| [Cloudinary](https://cloudinary.com/documentation/django_image_and_video_upload) | Django integration for image and video management with Cloudinary |
| [PIL](https://pillow.readthedocs.io/en/stable/) | Python Imaging Library for image processing |
| [Requests](https://docs.python-requests.org/en/master/) | Python library for making HTTP requests |
| [OpenAI API](https://beta.openai.com/docs/api-reference/introduction) | API reference for OpenAI |
| [Python datetime](https://docs.python.org/3/library/datetime.html) | Working with dates and times in Python |
| [Python io](https://docs.python.org/3/library/io.html) | Input and output in Python |
| [Python slugify](https://github.com/un33k/python-slugify) | Python library for converting strings to slugs |
| [Python image processing](https://docs.python.org/3/library/image.html) | Built-in Python library for image processing |
| [Updating Admin Portal Text](https://books.agiliq.com/projects/django-admin-cookbook/en/latest/change_text.html) | Changing text in Django admin portal |
| [Adding Messages with Django](https://docs.djangoproject.com/en/4.2/ref/contrib/messages/) | Adding messages in Django |
| [Django messages](https://django-messages.readthedocs.io/en/latest/) | Additional documentation for the Django messages framework |
| [BytesIO](https://docs.python.org/3/library/io.html) | Python library for working with bytes in memory |
| [Text Logo](https://www.w3schools.com/css/css3_3dtransforms.asp) | Creating a 3D text-based logo using CSS |
| [CSS Variables for Colour Palette](https://www.w3schools.com/css/css3_variables.asp) | Using CSS variables to create a custom color palette |
| [Loading Wheel for AI Art Generation & Wait Time Updates](https://loading.io/) | Loading wheel for AI art generation and wait time updates |
| [Aesthetically Pleasing Icons](https://fontawesome.com/search?q=next&o=r&m=free) | Font Awesome icons for use in the project |
| [Allow Only Registered Users to Download Images](https://docs.djangoproject.com/en/4.2/ref/templates/builtins/) | Django documentation for restricting access to registered users |
| [Disable Right Click on Images](https://www.dotnettricks.com/learn/aspnet/disable-right-click-on-web-page-and-images) | Tutorial on disabling right-click on images for added protection |


## Credits

In addition to the above documentation, I would like to give credit to the following resources: 

- __Code Institute__ - I've been learning how to code through the Code Institute, I found the information learned so far has given me the ability to create most of this project, I found the walk through Django Blog Project very helpful and it was used as the base for this project. 

- __Mentor__ - I found my three calls with my Code Institute mentor, Rohit, exceptionally valuable and useful.

- __ChatGPT__ - ChatGPT is relativly new technolgoy and needs to be used with a mountain of salt. Despite its inaccuracies, hallecanations and limitations, I found it a very useful resource when creating this project. I used it to assist with debugging and to point me in the direction of some of the coding requirements. It was particularliy useful when configuring the GenerateArt View, this took some trial and error before I had it functioning as intended. I also used ChatGPT to create the boilerplate data for the static about pages. I cross check information provided by ChatGPT with reputable resources to ensure the data being provided is reliable.

- __YouTube__ - I watached many videos on how to set up and use the OpenAI API, create Django projects, configure custom domains, etc. 

---

## Contact

I can be contacted directly at the following email address: 

- Kieran@KC-7.com