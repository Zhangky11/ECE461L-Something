from backend.shared.hardware_pool import HardwarePool
from backend.api.project.model import Project
from backend.auth.model import User
from backend.api.hardware.model import HwSet
from flask_mongoengine import MongoEngine
from flask import Blueprint, jsonify, request
from backend import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from mongoengine.queryset import Q
from bson import ObjectId

project_bp = Blueprint('project_bp', __name__)

@project_bp.route('/display_proj', methods=['POST', 'GET'])
@jwt_required()
def display_proj():
    print("Display Project Request!")
    raw_data = request.get_json()
    current_user = get_jwt_identity()
    project_id = raw_data.get('project_id')

    print(current_user)
    print(project_id)
    data = {}
    data['project_id'] = project_id

    if not Project.objects(id_inc=data['project_id']).first():
        print(f"no project {project_id}!!")
        return jsonify({"message": "Project doesn't exists"}), 400
    project = Project.objects(id_inc=data['project_id']).first()
    
    return_dict = {"username": current_user, 
                   "project_id": project.id_inc, 
                   'project_description': project.description,
                   "project_member_list": project.member_list, 
                   "Hardware_list": project.associated_hardwares()}
    
    print(return_dict)
    return jsonify(return_dict), 200

@project_bp.route('/create_proj', methods=['POST', 'GET'])
@jwt_required()
def create_proj():
    print("Create Project Request!")
    raw_data = request.get_json()
    current_user = get_jwt_identity()
    project_id = raw_data.get('project_id')
    project_name = raw_data.get('project_name')
    project_description = raw_data.get('project_description')

    data = {}
    data['username'] = current_user
    data['project_id'] = project_id
    data['project_name'] = project_name
    data['project_description'] = project_description


    # Hardcode for test use
    # for i in range(7):
    #     data = {}
    #     data['username'] = 'k'
    #     data['project_id'] = f"{i}"
    #     data['project_name'] = f"k's Project {i}"
    #     data['project_description'] = f"This is k's Project {i}"
    #     data['HwSet'] = []

    hw_from_pool1 = HardwarePool.objects(name="HW 1").first()
    hardware1 = HwSet(username=data['username'], 
                    project_id=data['project_id'],
                    hw_name="HW 1", 
                    hw_amount=0, 
                    hardware_from_pool=hw_from_pool1)
    hardware1.save()
    hw_from_pool2 = HardwarePool.objects(name="HW 2").first()
    hardware2 = HwSet(username=data['username'], 
                    project_id=data['project_id'],
                    hw_name="HW 2", 
                    hw_amount=0, 
                    hardware_from_pool=hw_from_pool2)
    hardware2.save()

    data['HwSet'] = [hardware1, hardware2]
    
    return_dict = {"HW_amount": [], "HW_availability": []}
    for hardware in HardwarePool.objects:
        return_dict["HW_amount"].append(0)
        return_dict["HW_availability"].append(hardware.total_availability)

    if not User.objects(username=data['username']).first():
        return jsonify({"message": "User doesn't exists"}), 400

    if Project.objects(id_inc=data['project_id']).first():
        return jsonify({"message": "Project already exist"}),400
    
    user = User.objects(username=data['username']).first()

    project = Project(name=data['project_name'], 
                    description=data['project_description'], 
                    joined_hwsets = data['HwSet'], 
                    id_inc=data['project_id'])
    project.member_list.append(user.username)
    project.save()
    user.joined_projects.append(project)
    user.save()

    return_dict["message"] = "Create project successfully"
    return jsonify(return_dict), 200


@project_bp.route('/join_proj', methods=['POST', 'GET'])
@jwt_required()
def join_proj():
    print("Join Project Request!")
    raw_data = request.get_json()
    current_user = get_jwt_identity()
    project_id = raw_data.get('project_id')
    data = {}
    data['username'] = current_user
    data['project_id'] = project_id

    if not User.objects(username=data['username']).first():
        return jsonify({"message": "User doesn't exists"}), 400
    
    user = User.objects(username=data['username']).first()

    if not Project.objects(id_inc=data['project_id']).first():
        return jsonify({"message": "Project doesn't exists"}), 400
    
    project = Project.objects(id_inc=data['project_id']).first()

    if project in user.joined_projects:
        return jsonify({"message": "You have already joined the project"}), 400

    user.joined_projects.append(project)
    user.save()
    project.member_list.append(user.username)
    project.save()
    return jsonify({"message": "Join project successfully"}), 200

@project_bp.route('/delete_proj', methods=['POST', 'GET'])
@jwt_required()
def delete_proj():
    #memberlist
    #hardwareset
    raw_data = request.get_json()
    current_user = get_jwt_identity()
    project_id = raw_data.get('project_id')
    data = {}
    data['username'] = current_user
    data['project_id'] = project_id
    
    project = Project.objects(id_inc=data['project_id']).first()
    #objid = project.id
    
    if not project:
        return jsonify({"message": "Project doesn't exists"}), 400
    
    
    # Query the User collection to find documents with the specified value in their memberList
    if not data['username'] in project.member_list:
        return jsonify({"message": "User isn't in the project"}), 400
    

    for user in project.member_list:
        if User.objects(username=user).first():
            User.objects(username = user).first().update(pull__joined_projects=project)
    
    
    for hw in project.joined_hwsets:
        hw_ref = hw.id
        hw_id = ObjectId(hw_ref)
        print(hw_id)
        if HwSet.objects(id = hw_id).first():
            currentHardware = HwSet.objects(id=hw_id).first()
            Hardware_name = currentHardware.get_name()
            print(Hardware_name)
            Hardware_amount = currentHardware.get_totalamount()
            print(Hardware_amount)
            HardwarePool.objects(name=Hardware_name).first().return_hardware(Hardware_amount)
            currentHardware.delete()
    project.delete()
    return jsonify({"message": "Delete project successfully"}), 200
    
@project_bp.route('/leave_proj', methods=['POST', 'GET'])
@jwt_required()
def leave_proj():

    raw_data = request.get_json()
    current_user = get_jwt_identity()
    project_id = raw_data.get('project_id')
    data = {}
    data['username'] = current_user
    data['project_id'] = project_id

    if not User.objects(username=data['username']).first():
        return jsonify({"message": "User doesn't exists"}), 400
    
    user = User.objects(username=data['username']).first()

    if not Project.objects(id_inc=data['project_id']).first():
        return jsonify({"message": "Project doesn't exists"}), 400
    
    project = Project.objects(id_inc=data['project_id']).first()
    user.update(pull__joined_projects=project)
    project.update(pull__member_list=data['username'])
    return jsonify({"message": "Leave project successfully"}), 200

