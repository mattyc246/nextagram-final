from flask import Blueprint, flash, redirect, url_for
from models.follower_following import FollowerFollowing
from models.user import User
from flask_login import login_required, current_user

follower_following_blueprint = Blueprint(
    'follower_following', __name__, template_folder='templates')


@follower_following_blueprint.route('/<idol_id>/follow', methods=['GET'])
@login_required
def follow(idol_id):
    idol = User.get_or_none(User.id == idol_id)
    fan = User.get_or_none(User.id == current_user.id)

    if not fan or not idol:
        flash("Oopsies, we couldn't understand your request", "warning")
        return redirect(url_for('users.index'))

    follow = FollowerFollowing(
        idol_id=idol.id,
        fan_id=fan.id
    )

    if not idol.private:
        follow.approved = True

    if not follow.save():
        flash('Something went wrong, try again', 'warning')
        return redirect(url_for('users.show', username=idol.username))

    flash(f'You are now following {idol.username}', 'success')
    return redirect(url_for('users.show', username=idol.username))


@follower_following_blueprint.route('/<idol_id>/unfollow', methods=['GET'])
@login_required
def unfollow(idol_id):
    follow = FollowerFollowing.get_or_none(
        (FollowerFollowing.idol_id == idol_id) &
        (FollowerFollowing.fan_id == current_user.id)
    )

    idol = User.get_or_none(User.id == idol_id)

    if not follow:
        flash('Oops, something went wrong', 'warning')
        return redirect(url_for('users.show', username=idol.username))

    if not follow.delete_instance():
        flash('Oops, something went wrong', 'warning')
        return redirect(url_for('users.show', username=idol.username))

    flash(f'You have unfollowed {idol.username}', 'success')
    return redirect(url_for('users.show', username=idol.username))
