import tornado
import tornado.web
import tornado.auth
import base_handler
import jsonhandler
import sys


class CharacterFormHandler(jsonhandler.JsonHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write(self._character_form.get_str_all())
        self.finish()


class CharacterViewHandler(jsonhandler.JsonHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        if not self.is_permission_admin() and self._global_arg["disable_user_character"] or \
                self._global_arg["disable_character"]:
            # Not Found
            self.set_status(404)
            self.send_error(404)
            raise tornado.web.Finish()

        # validate argument
        is_admin = self.request.query == "is_admin"
        # user_id = self.request.query[len("user_id="):]
        # if user_id == "" and not is_admin:
        #     # Forbidden
        #     self.set_status(403)
        #     self.send_error(403)
        #     raise tornado.web.Finish()

        # validate permission and send result
        if is_admin:
            if self.is_permission_admin():
                data = json.dumps(self._db.get_all_user())
            else:
                print("Insufficient permissions from %s" % self.request.remote_ip, file=sys.stderr)
                # Forbidden
                self.set_status(403)
                self.send_error(403)
                raise tornado.web.Finish()
        else:
            user_id = self.current_user.get("user_id", "")
            if not user_id:
                print("Insufficient permissions from %s" % self.request.remote_ip, file=sys.stderr)
                # Forbidden
                self.set_status(403)
                self.send_error(403)
                raise tornado.web.Finish()

            data = json.dumps(self._db.get_all_user(user_id=user_id))

        self.write(data)
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        if self._global_arg["disable_character"]:
            # Not Found
            self.set_status(404)
            self.send_error(404)
            raise tornado.web.Finish()
        self.prepare_json()

        user = self.get_argument("player")
        character = self.get_argument("character")
        delete_user_by_id = self.get_argument("delete_user_by_id")
        delete_character_by_id = self.get_argument("delete_character_by_id")

        # exception, if delete_user_by_id, create user if not exist
        if not user and delete_user_by_id:
            user = {"user_id": delete_user_by_id}

        self._db.update_user(user, character, delete_user_by_id=delete_user_by_id,
                             delete_character_by_id=delete_character_by_id)