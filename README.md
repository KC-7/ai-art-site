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
