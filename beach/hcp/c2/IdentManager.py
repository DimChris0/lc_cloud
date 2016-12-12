# Copyright 2015 refractionPOINT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from beach.actor import Actor
import traceback
import hashlib
import time
import uuid
CassDb = Actor.importLib( 'utils/hcp_databases', 'CassDb' )
CassPool = Actor.importLib( 'utils/hcp_databases', 'CassPool' )

class IdentManager( Actor ):
    def init( self, parameters, resources ):
        self.admin_oid = parameters.get( 'admin_oid', None )
        if self.admin_oid is None: raise Exception( 'Admin OID must be specified.' )

        self._db = CassDb( parameters[ 'db' ], 'hcp_analytics', consistencyOne = True )
        self.db = CassPool( self._db,
                            rate_limit_per_sec = parameters[ 'rate_limit_per_sec' ],
                            maxConcurrent = parameters[ 'max_concurrent' ],
                            blockOnQueueSize = parameters[ 'block_on_queue_size' ] )

        self.db.start()

        self.audit = self.getActorHandle( resources[ 'auditing' ] )
        self.page = self.getActorHandle( resources[ 'paging' ] )

        self.handle( 'authenticate', self.authenticate )
        self.handle( 'create_user', self.createUser )
        self.handle( 'delete_user', self.deleteUser )
        self.handle( 'change_password', self.changePassword )
        self.handle( 'create_org', self.createOrg )
        self.handle( 'add_user_to_org', self.addUserToOrg )
        self.handle( 'remove_user_from_org', self.removeUserFromOrg )
        self.handle( 'get_org_info', self.getOrgInfo )
        self.handle( 'get_org_members', self.getOrgMembers )
        self.handle( 'get_user_membership', self.getUserMembership )
        self.handle( 'get_user_info', self.getUserInfo )
        
    def deinit( self ):
        pass

    def asUuidList( self, elem ):
        if type( elem ) not in ( list, tuple ):
            elem = [ elem ]
        return map( uuid.UUID, elem )

    def authenticate( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        password = req[ 'password' ]

        isAuthenticated = False
        info = self.db.getOne( 'SELECT uid, email, salt, salted_password, is_deleted, must_change_password FROM user_info WHERE email = %s', 
                               ( email, ) )

        if info is None or info[ 4 ] is True:
            return ( True, { 'is_authenticated' : False } )

        uid, email, salt, salted_password, is_deleted, must_change_password = info

        if hashlib.sha256( '%s%s' % ( password, salt ) ).hexdigest() != salted_password:
            return ( True, { 'is_authenticated' : False } )

        orgs = []
        info = self.db.execute( 'SELECT oid FROM org_membership WHERE uid = %s', ( uid, ) )
        if info is not None:
            for row in info:
                orgs.append( row[ 0 ] )

        for oid in orgs:
            self.audit.shoot( 'record', { 'oid' : oid, 'etype' : 'login', 'msg' : 'User %s logged in.' % email } )

        return ( True, { 'is_authenticated' : True, 'uid' : uid, 'email' : email, 'orgs' : orgs, 'must_change_password' : must_change_password } )

    def createUser( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        password = req[ 'password' ]
        byUser = req[ 'by' ]
        uid = uuid.uuid4()
        salt = hashlib.sha256( str( uuid.uuid4() ) ).hexdigest()
        salted_password = hashlib.sha256( '%s%s' % ( password, salt ) ).hexdigest()

        info = self.db.getOne( 'SELECT uid, is_deleted FROM user_info WHERE email = %s', ( email, ) )
        if info is not None and info[ 1 ] is not True:
            return ( True, { 'is_created' : False } )

        self.db.execute( 'INSERT INTO user_info ( email, uid, salt, salted_password, is_deleted, must_change_password ) VALUES ( %s, %s, %s, %s, false, true )', 
                         ( email, uid, salt, salted_password ) )

        self.audit.shoot( 'record', { 'oid' : self.admin_oid, 'etype' : 'user_create', 'msg' : 'User %s created by %s.' % ( email, byUser ) } )

        return ( True, { 'is_created' : True, 'uid' : uid } )

    def deleteUser( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        byUser = req[ 'by' ]

        info = self.db.getOne( 'SELECT uid FROM user_info WHERE email = %s', ( email, ) )
        if info is None:
            return ( True, { 'is_deleted' : False } )

        uid = info[ 0 ]

        self.db.execute( 'UPDATE user_info SET is_deleted = true WHERE email = %s', 
                         ( email, ) )

        self.audit.shoot( 'record', { 'oid' : self.admin_oid, 'etype' : 'user_deleted', 'msg' : 'User %s deleted by %s.' % ( email, byUser ) } )

        return ( True, { 'is_deleted' : True, 'uid' : uid } )

    def changePassword( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        password = req[ 'password' ]
        byUser = req[ 'by' ]
        salt = hashlib.sha256( str( uuid.uuid4() ) ).hexdigest()
        salted_password = hashlib.sha256( '%s%s' % ( password, salt ) ).hexdigest()

        info = self.db.getOne( 'SELECT uid FROM user_info WHERE email = %s', ( email, ) )
        if info is None:
            return ( True, { 'is_changed' : False } )

        uid = info[ 0 ]

        self.db.execute( 'UPDATE user_info SET salt = %s, salted_password = %s, must_change_password = false WHERE email = %s', 
                         ( salt, salted_password, email ) )

        self.audit.shoot( 'record', { 'oid' : self.admin_oid, 'etype' : 'password_change', 'msg' : 'User %s password changed by %s.' % ( email, byUser ) } )

        return ( True, { 'is_changed' : True, 'uid' : uid } )

    def createOrg( self, msg ):
        req = msg.data

        name = req[ 'name' ]
        byUser = req[ 'by' ]
        oid = uuid.uuid4()

        self.db.execute( 'INSERT INTO org_info ( oid, name ) VALUES ( %s, %s )', ( oid, name ) )

        self.audit.shoot( 'record', { 'oid' : self.admin_oid, 'etype' : 'org_create', 'msg' : 'Org %s ( %s ) created by %s.' % ( name, oid, byUser ) } )

        return ( True, { 'is_created' : True, 'oid' : oid } )

    def addUserToOrg( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        oid = uuid.UUID( req[ 'oid' ] )
        byUser = req[ 'by' ]

        info = self.db.getOne( 'SELECT uid FROM user_info WHERE email = %s', ( email, ) )
        if info is None:
            return ( True, { 'is_added' : False } )
        uid = info[ 0 ]

        self.db.execute( 'INSERT INTO org_membership ( uid, oid ) VALUES ( %s, %s )', 
                         ( uid, oid ) )

        self.audit.shoot( 'record', { 'oid' : oid, 'etype' : 'org_user', 'msg' : 'User %s added to org by %s.' % ( email, byUser ) } )

        allUsers = self.db.execute( 'SELECT uid FROM org_membership WHERE oid = %s', ( oid, ) )
        if allUsers is not None:
            for row in allUsers:
                userInfo = self.db.getOne( 'SELECT email FROM user_info WHERE uid = %s', ( row[ 0 ], ) )
                self.page.shoot( 'page', 
                                 { 'to' : userInfo[ 0 ], 
                                   'msg' : 'The user %s has been added to the organization %s by %s.' % ( email, oid, byUser ), 
                                   'subject' : 'User added to org' } )

        return ( True, { 'is_added' : True } )

    def removeUserFromOrg( self, msg ):
        req = msg.data

        email = req[ 'email' ]
        oid = uuid.UUID( req[ 'oid' ] )
        byUser = req[ 'by' ]

        info = self.db.getOne( 'SELECT uid FROM user_info WHERE email = %s', ( email, ) )
        if info is None:
            return ( True, { 'is_removed' : False } )
        uid = info[ 0 ]

        res = self.db.getOne( 'SELECT uid FROM org_membership WHERE uid = %s AND oid = %s', 
                              ( uid, oid ) )
        if res is not None:
            return ( True, { 'is_removed' : False } )

        self.db.execute( 'DELETE FROM org_membership WHERE uid = %s AND oid = %s', 
                         ( uid, oid ) )

        self.audit.shoot( 'record', { 'oid' : oid, 'etype' : 'org_user', 'msg' : 'User %s removed from org by %s.' % ( email, byUser ) } )

        allUsers = self.db.execute( 'SELECT uid FROM org_membership WHERE oid = %s', ( oid, ) )
        if allUsers is not None:
            for row in allUsers:
                userInfo = self.db.getOne( 'SELECT email FROM user_info WHERE uid = %s', ( row[ 0 ], ) )
                self.page.shoot( 'page', 
                                 { 'to' : userInfo[ 0 ], 
                                   'msg' : 'The user %s has been removed from organization %s by %s.' % ( email, oid, byUser ), 
                                   'subject' : 'User added to org' } )

        return ( True, { 'is_removed' : True } )

    def getOrgInfo( self, msg ):
        req = msg.data

        isAll = req.get( 'include_all', False )

        if not isAll:
            oid = self.asUuidList( req[ 'oid' ] )
        else:
            oid = []

        info = self.db.execute( 'SELECT name, oid FROM org_info' )
        if info is None:
            return ( False, 'error getting org info' )

        orgs = []
        for row in info:
            if row[ 1 ] in oid or isAll:
                orgs.append( ( row[ 0 ], row[ 1 ] ) )

        return ( True, { 'orgs' : orgs } )

    def getOrgMembers( self, msg ):
        req = msg.data

        oids = self.asUuidList( req[ 'oid' ] )
        
        membership = {}
        for oid in oids:
            info = self.db.execute( 'SELECT oid, uid FROM org_membership WHERE oid = %s', ( oid, ) )
            if info is None:
                return ( False, 'error getting org membership' )

            for row in info:
                membership.setdefault( row[ 0 ], {} ).setdefault( row[ 1 ], None )

        for oid, org in membership.iteritems():
            for uid in org:
                info = self.db.getOne( 'SELECT email FROM user_info WHERE uid = %s', ( uid, ) )
                if info is None:
                    return ( False, 'error getting user info' )
                org[ uid ] = info[ 0 ]

        return ( True, { 'orgs' : membership } )

    def getUserMembership( self, msg ):
        req = msg.data

        uid = uuid.UUID( req[ 'uid' ] )

        orgs = []
        info = self.db.execute( 'SELECT oid FROM org_membership WHERE uid = %s', ( uid, ) )
        if info is not None:
            for row in info:
                orgs.append( row[ 0 ] )

        return ( True, { 'uid' : uid, 'orgs' : orgs } )

    def getUserInfo( self, msg ):
        req = msg.data

        uids = self.asUuidList( req[ 'uid' ] )

        res = {}

        for uid in uids:
            info = seld.db.getOne( 'SELECT uid, email FROM user_info WHERE uid = %s', ( uid, ) )
            if not info:
                return ( False, 'error getting user info' )
            res[ info[ 0 ] ] = info[ 1 ]
        return ( True, res )

