from flask import Flask, render_template, request, redirect, make_response, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
from flask_socketio import SocketIO