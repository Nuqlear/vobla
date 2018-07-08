# ![](https://drone.olegshigor.in/api/badges/Nuqlear/vobla/status.svg?branch=master) vobla

Vobla is a simple file sharing self-hosted solution.  
There are two available desktop clients: [vobla-win](https://github.com/nuqlear/vobla-win) and [ShareX](https://github.com/ShareX/ShareX) (.sxcu for it served from /sharex).

## Screenshots

<img src="https://raw.githubusercontent.com/Nuqlear/vobla/master/.github/login.png" width="33%"><img src="https://raw.githubusercontent.com/Nuqlear/vobla/master/.github/dashboard.png" width="33%"/><img src="https://raw.githubusercontent.com/Nuqlear/vobla/master/.github/drop.png" width="33%">

## How to run

```bash
$ make build && make up
$ make shell
$ python manage.py createinv && exit
```

Now you can sign up with invite code from stdout.
