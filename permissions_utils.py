from django.contrib.auth.models import User, Group, Permission
from django.template.library import InvalidTemplateLibrary,Library,TagHelperNode

def get_group_permissions(user):
    user_groups = user.groups.all()
    group_permissions = []

    for group in user_groups:
        group_permissions.extend(group.permissions.all())

    return group_permissions




# i have a file permissions_utils.py  which is in root directory.

# from django.contrib.auth.models import User, Group, Permission
# def get_group_permissions(user):
#     user_groups = user.groups.all()
#     group_permissions = []

#     for group in user_groups:
#         group_permissions.extend(group.permissions.all())

#     return group_permissions


# admin.py for example

# def has_view_permission(self, request, obj=None):
#         user_group_permissions = get_group_permissions(request.user)
#         desired_permission_codename = 'view_orderstatus'
#         if any(perm.codename == desired_permission_codename for perm in user_group_permissions):
#             return True
#         else:
#             return False



# as i done the group permission in admin.py in my project  i want to done the same in my base.hmtl
# <li class="nav-header">
#   <span class="menu-toggle"><svg xmlns="http://www.w3.org/2000/svg" height="2em" viewBox="0 0 448 512"><style>svg{fill:#ffffff}</style></svg>
#       <p>Order Management</p> </span>
#   <ul class="subcategory">


#       <li class="nav-item">
#           <a href="{% url 'admin:product_order_changelist' %}" class="nav-link">
#               <i class="nav-icon fas fa-users"></i> <p>Order Details</p>
#           </a>
#       </li>


#       <li class="nav-item">
#           <a href="/admin/setting/orderstatus/" class="nav-link">
#               <i class="nav-icon fas fa-circle"></i> <p>Order Status</p>
#           </a>
#       </li>


#   </ul>
# </li>



