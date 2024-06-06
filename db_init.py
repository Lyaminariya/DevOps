from app import app, db
from db_models import User, Profile, Case, Item
from werkzeug.security import generate_password_hash


# DB drop, creating, filling some things

def db_create():
    with app.app_context():
        db.drop_all()
        db.create_all()

        db.session.add(User(name="sergey", password=generate_password_hash("123456789")))
        db.session.add(Profile(user_id=1, email="lyamkin.serega@mail.ru", avatar_href="https://flyclipart.com/thumb2"
                                                                                      "/avatar-icon-518360.png"))
        db.session.add(User(name="timothy", password=generate_password_hash("12345678")))
        db.session.add(
            Profile(user_id=2, email="timofey.bolotov@mail.ru", avatar_href="https://flyclipart.com/thumbs/med"
                                                                            "-boukrima-specialist-webmaster"
                                                                            "-php-e-commerce-web-developer"
                                                                            "-coder-avatar-1054388.png"))
        db.session.add(User(name="ivan", password=generate_password_hash("1234567")))
        db.session.add(Profile(user_id=3, email="ivan.terekhov@mail.ru", avatar_href="https://yt3.googleusercontent.com"
                                                                                     "/ytc"
                                                                                     "/AL5GRJXcAA8ixtLeaCZUzoUjqVcaoiNg"
                                                                                     "5dcbWMPsjE8T=s900-c-k"
                                                                                     "-c0x00ffffff-"
                                                                                     "no-rj"))
        db.session.add(Case(name="Нищий", image_path="https://yt3.ggpht.com/ytc/AMLnZu"
                                                     "-WY6rnFBTc2xnAKnXJWOJGgLtjH415ONsoH0pn"
                                                     "=s900-c-k-c0x00ffffff-no-rj", user_id=1))
        db.session.add(Case(name="Норм", image_path="https://gocsgo.net/wp-content/uploads/2021/11/cs20-case.jpg",
                            user_id=2))
        db.session.add(
            Case(name="Про", image_path="https://sun6-23.userapi.com/impg/SE0BqlcUbyL8YA7QPLB4pfKpTpTfGr-wurz"
                                        "-Iw/PlJQwKjd8n0.jpg?size=0x160&crop=0.102,0.008,0.792,"
                                        "0.98&quality=95&sign=c978983626c35c415ce430918b4f9721", user_id=3))
        db.session.add(Item(name="Шырокий пистолет", image_path="https://avatars.mds.yandex.net/i?id"
                                                                "=320efb941be61e53949fdcd00e3cd8fb38e51093-7552222"
                                                                "-images"
                                                                "-thumbs&n=13", case_id=1, user_id=1))
        db.session.add(Item(name="Hell No", image_path="https://flyclipart.com/thumb2/image-675160.png", case_id=1,
                            user_id=1))
        db.session.add(Item(name="Револьверо", image_path="https://cdna.artstation.com/p/assets/images/images/000"
                                                          "/667/542/large/thomas-butters-2015-04-29-16-22-42.jpg"
                                                          "?1430321151", case_id=1, user_id=1))
        db.session.add(
            Item(name="Калашик?", image_path="https://i.ytimg.com/vi/W-JHitgmoSE/maxresdefault.jpg", case_id=2,
                 user_id=2))
        db.session.add(Item(name="Эмочка", image_path="https://media.sketchfab.com/models"
                                                      "/9bb8f18ad94d4b468e447a2d43bd08b9/thumbnails"
                                                      "/bf2178d8e9064b5680f76c5a3e9f1b06"
                                                      "/bcfe58e4822449b5b2ea286d771f57a8"
                                                      ".jpeg", case_id=2, user_id=2))
        db.session.add(Item(name="В голову", image_path="https://media.sketchfab.com/models"
                                                        "/c3d9d9a97374444ea0e2333dea0fcf2c/thumbnails"
                                                        "/1cdab5ea346644648d9d392c37f8cee1"
                                                        "/64a896b965384668989743f86b171e87.jpeg", case_id=2,
                            user_id=2))
        db.session.add(Item(name="Новый автомат", image_path="https://sun9-32.userapi.com/impg"
                                                             "/Cxfy8lAVY98gMjFDdOLMiec0KyFPyxI3J1sZ2g/b3rNXMhJvlo"
                                                             ".jpg?size=1600x900&quality=96&sign"
                                                             "=4aa4dfd65a6fbe26e291b9e8e1532947&c_uniq_tag"
                                                             "=750h4_S80fCRtdDwYxDzE4NRAlP1-tNDSM-u3Sbi1mk&type"
                                                             "=album", case_id=3, user_id=3))
        db.session.add(Item(name="Точно в жбан!", image_path="https://img2.joyreactor.cc/pics/comment/full"
                                                             "/снайпер-снайперская-винтовка"
                                                             "-сосулька-воображение-4539449.jpeg", case_id=3,
                            user_id=3))
        db.session.add(Item(name="Zero chances", image_path="https://i.ytimg.com/vi/"
                                                            "PtMkeAkjhNk/maxresdefault.jpg", case_id=3, user_id=3))
        db.session.commit()


db_create()
