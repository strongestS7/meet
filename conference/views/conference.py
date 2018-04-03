from flask import Flask, Blueprint, session, redirect, render_template, request, views
import datetime, json
from .. import db
from .. import models

blue_conference = Blueprint('blue_book', __name__, template_folder='templates', static_folder='static')


# @blue_conference.route('/conference', methods=['GET', 'POST','DELETE'])
# def conference():
#     if request.method == 'POST':
#         ret = {'status':None,'msg':''}
#         try:
#             # 选定按钮，添加到数据库
#             data_list = json.loads(request.form.get('data_list'))
#             data_list[0]['user_id'] = session.get('user_id')
#             print(data_list)
#             # 整理数据
#             # data_list = [(i['conference_date'], int(i['homes_id']), user_id, int(i['conference_time_id'])) for i in data_list]
#             # sql = 'insert into record(conference_date,homes_id,user_id,conference_time_id) VALUES(%s,%s,%s,%s)'
#             # ret = SQLHelper.create_many(sql, args=data_list)
#
#             record = models.Record(**data_list[0])
#             db.session.add(record)
#             db.session.commit()
#
#             ret['status'] = True
#         except Exception as e:
#             ret['msg'] = '预订异常'
#
#         return json.dumps(ret)
#
#     if request.method == 'GET':
#         try:
#             current_user_id = session.get('user_id')
#             current_user = session.get('user_info')[0]
#
#             # 获取url中date数据，没有则取当天
#             ctime = request.args.get('date')
#             ctime = ctime or datetime.date.today()
#
#             # 时间段表
#             time_list = db.session.query(models.ConferenceTime).all()
#
#             # 房间表
#             homes_list = db.session.query(models.Homes).all()
#
#             # 记录表
#             record_list = db.session.query(models.Record).filter(models.Record.conference_date == ctime).all()
#             record_dict = {(i.homes_id, i.conference_time_id): {'user_id':i.user_id,'record_id':i.id} for i in record_list}
#
#             return render_template('book.html',
#                                    record_dict=record_dict,
#                                    time_list=time_list,
#                                    homes_list=homes_list,
#                                    current_user_id=current_user_id,
#                                    current_user=current_user,
#                                    ctime=ctime, )
#         except Exception as e:
#             return '请求异常'
#
#     if request.method == 'DELETE':
#         ret = {'status': None, 'msg': ''}
#         try:
#             record_id = request.form.get('record_id')
#             user_id = session.get('user_id')
#
#             db.session.query(models.Record).filter(models.Record.id==record_id,models.Record.user_id==user_id).delete()
#             db.session.commit()
#             ret['status'] = True
#
#         except Exception as  e:
#             ret['msg'] = e
#
#         return json.dumps(ret)


class Conference(views.MethodView):
    methods = ['GET', 'POST', 'DELETE']

    def get(self):
        """展示"""
        try:
            current_user_id = session.get('user_id')
            current_user = session.get('user_info')[0]

            # 获取url中date数据，没有则取当天
            ctime = request.args.get('date')
            ctime = ctime or datetime.date.today()

            # 时间段表
            time_list = db.session.query(models.ConferenceTime).all()

            # 房间表
            homes_list = db.session.query(models.Homes).all()

            # 记录表
            record_list = db.session.query(models.Record).filter(models.Record.conference_date == ctime).all()
            record_dict = {(i.homes_id, i.conference_time_id): {'user_id': i.user_id, 'record_id': i.id} for i in
                           record_list}

            return render_template('book.html',
                                   record_dict=record_dict,
                                   time_list=time_list,
                                   homes_list=homes_list,
                                   current_user_id=current_user_id,
                                   current_user=current_user,
                                   ctime=ctime, )
        except Exception as e:
            return '请求异常'

    def post(self):
        """添加"""
        ret = {'status': None, 'msg': ''}
        try:
            # 选定按钮，添加到数据库
            data_list = json.loads(request.form.get('data_list'))
            user_id = session.get('user_id')

            conference_date_str = data_list[0].get('conference_date')
            conference_date = datetime.datetime.strptime(conference_date_str, "%Y-%m-%d").date()
            print('data_list',data_list)
            # print('conference_date====>',conference_date)

            if conference_date < datetime.date.today():
                raise ValueError('不能预订以前的')

            # 添加数据
            record_list = [models.Record(**data, user_id=user_id) for data in data_list]
            for i in record_list:
                print(i.homes_id,i.conference_time_id,i.conference_date,i.user_id)
            print(user_id)
            print('>>>>>>>>>',record_list)
            db.session.add_all(record_list)
            db.session.commit()
            db.session.close()
            ret['status'] = True
            print('===true====')
        except ValueError as e:
            print(e)
            ret['msg'] = str(e)

        except Exception as e:
            print(e)
            ret['msg'] = '预订异常'

        return json.dumps(ret)

    def delete(self):
        """取消"""
        ret = {'status': None, 'msg': ''}
        try:
            record_id = request.form.get('record_id')
            user_id = session.get('user_id')

            record = db.session.query(models.Record).filter(models.Record.id == record_id,
                                                   models.Record.user_id == user_id)
            if record[0].conference_date < datetime.date.today():
                raise ValueError('已过期,不能取消')
            else:
                record.delete()
                db.session.commit()
                ret['status'] = True

        except ValueError as e:
            print(e)
            ret['msg'] = str(e)

        except Exception as  e:
            print(e)
            ret['msg'] = str(e)

        return json.dumps(ret)


blue_conference.add_url_rule('/conference', view_func=Conference.as_view(name='conference'))


@blue_conference.before_request
def is_login(*args, **kwargs):
    user = session.get('user_info')
    if user:
        return None
    return redirect('/login')
