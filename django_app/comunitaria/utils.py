# -*- coding: utf-8 -*-
from comunitaria.models import (Community, UserCommunity)
from rest_framework.response import Response

def check_user_comm_permissions(request, community_id):
    """
        Auxiliar function to check if user belongs to the Community or if user
        is superuser.

        Returns: allowed, Response
    """
    if not request.user.is_authenticated:
        err_msg = _(u'You need to be logged !')
        return False, Response([{'error': True, 'error_text': err_msg}])

    user_communities_id = request.user.communities.all()
    user_communities_id = user_communities_id.values_list("community__id",
                                                          flat=True)
    if (int(community_id) not in user_communities_id) and \
            not request.user.is_superuser and not request.user.is_staff:
        err_msg = _(u"You don't belong to this community !")
        return False, Response({'error': True, 'error_text': err_msg})

    try:
        community = Community.objects.get(id=community_id)
    except Exception:
        err_msg = _(u'Unable to find community')
        return False, Response({'error': True, 'error_text': err_msg})

    if not request.user.communities.get(community=community).is_active:
        err_msg = _(u"You are not active yet to operate with this community!")
        return False, Response({'error': True, 'error_text': err_msg})
    
    return True, ""

