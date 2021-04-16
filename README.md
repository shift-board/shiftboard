# Shiftboard

Shiftboard is a web application that allows a user to create boards for other, anonymous users to put messages and pictures related to the board. The users posting do not need to make an account at all, but can optionally leave their name with their post. Great for something like virtual birthday wishes or memorials!

A board can have multiple admin users who will be able to moderate and delete inappropriate boards. Be careful with a board link, as anyone with the link is able to make posts. Boards will have their associated UUID in the URL instead of using an incremental system.

This project was made for Zhang Xian Kai :)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) and install the requirements, then run the server.

```bash
python -m pip install -r requirements.txt
python manage.py runserver
```

## Roadmap
Shiftboard is currently in development! Here is a quick roadmap of what we have planned:

### Shiftboard v0.1
- [x] Working database with boards and posts
- [ ] Creation of posts possible
- [ ] Able to see posts, and if you click on posts they pop up with the message
- [ ] Mobile and web functionality
- [ ] Posts and boards are saved
- [ ] Easy and convenient add post section
- [ ] Admin users can delete posts
- [x] For Zhang Xian Kai

### Shiftboard v1.0
- [ ] Able to create boards and generate a board URL to visit each board
- [ ] User account creation to create boards and determine admins
- [ ] Hosted on [Heroku](https://www.heroku.com/)

## Support
Found an issue? Report it on the issues tab!

## License
[MIT](https://choosealicense.com/licenses/mit/)
