/* Add your header comment here */
#include <sqlite3ext.h> /* Do not use <sqlite3.h>! */
#include <stdio.h>
#include <stdlib.h>
#include "blockcachevfs.h"
SQLITE_EXTENSION_INIT1

/* Insert your extension code here */

#ifdef _WIN32
__declspec(dllexport)
#endif

#define CS_STORAGE "google?emulator=127.0.0.1:4443"
#define CS_ACCOUNT getenv("CS_ACCOUNT")
#define CS_KEY getenv("CS_KEY")
#define CACHE_DIR getenv("SQ_CACHE_DIR")
#define VFS_NAME getenv("SQ_VFS_NAME")
#define DB_BUCKET getenv("SQ_DB_BUCKET")
#define LOCAL_CONTAINER_ALIAS getenv("SQ_CONTAINER_ALIAS")

static int csAuthCb(
  void *pCtx,
  const char *zStorage,
  const char *zAccount,
  const char *zContainer,
  char **pzAuthToken
){
  *pzAuthToken = sqlite3_mprintf("%s", CS_KEY);
  return (*pzAuthToken) ? SQLITE_OK : SQLITE_NOMEM;
}


/* TODO: Change the entry point name so that "extension" is replaced by
** text derived from the shared library filename as follows:  Copy every
** ASCII alphabetic character from the filename after the last "/" through
** the next following ".", converting each character to lowercase, and
** discarding the first three characters if they are "lib".
*/

int init_vfs(sqlite3 *db, char **pzErrMsg) {
    const char* env_key = getenv("CS_KEY");
    if (env_key == NULL) {
        if (pzErrMsg) {
            *pzErrMsg = sqlite3_mprintf("Auth token (CS_KEY) environment variable not set.");
        }
        return SQLITE_ERROR; 
    }

    int rc = SQLITE_OK;
    sqlite3_bcvfs *pVfs_ = NULL;

    // Use a local error message pointer for bcvfs calls 
    char *localBcvfsErrMsg = NULL; 

    pVfs_ = (sqlite3_bcvfs *)sqlite3_vfs_find(VFS_NAME);
    
    if (pVfs_ == NULL) {
        // Pass the address of the local error pointer
        rc = sqlite3_bcvfs_create(CACHE_DIR, VFS_NAME, &pVfs_, &localBcvfsErrMsg); 
    } else {
        // Cleanup the local error message pointer if it was set
        if (localBcvfsErrMsg != NULL) {
            // You MUST free the memory allocated by the bcvfs library for its error messages
            sqlite3_free(localBcvfsErrMsg); // Assuming bcvfs uses sqlite3_malloc for errors
            // If the bcvfs library uses standard C malloc(), use free(localBcvfsErrMsg);
        }
        return SQLITE_OK;
    }
    

    if( rc==SQLITE_OK && pVfs_ != NULL ){ 
        // ... (daemon checks and config calls are fine) ...
        sqlite3_bcvfs_config(pVfs_, SQLITE_BCV_CURLVERBOSE, 0); 
        
        if( rc==SQLITE_OK ){
            sqlite3_bcvfs_auth_callback(pVfs_, 0, csAuthCb);
        }
        
        if( rc==SQLITE_OK ){
            // Pass the address of the local error pointer again
            rc = sqlite3_bcvfs_attach(pVfs_, CS_STORAGE, CS_ACCOUNT, DB_BUCKET, LOCAL_CONTAINER_ALIAS,
                SQLITE_BCV_ATTACH_IFNOT, &localBcvfsErrMsg 
            );
            // Check attach error
            if (rc != SQLITE_OK && localBcvfsErrMsg != NULL) {
                 printf("attach error: %s\n", localBcvfsErrMsg);
            }
        }
        if( rc==SQLITE_OK ){
            rc = sqlite3_bcvfs_register_vtab(db);
        } else {
            printf("Could not register virtual table\n");
        }
        

        sqlite3_vfs_register((sqlite3_vfs *)pVfs_, 0);
        

    } else {
        printf("VFS creation failed with return code %d\n", rc);
    };
    // Cleanup the local error message pointer if it was set 
    if (localBcvfsErrMsg != NULL) {
        sqlite3_free(localBcvfsErrMsg); 
    }

    // If we return an error to SQLite, *we* need to set *pzErrMsg 
    if (rc != SQLITE_OK && pzErrMsg != NULL) {
        *pzErrMsg = sqlite3_mprintf("init_vfs failed with generic error code: %d", rc);
    }

    return rc;
}
int sqlite3_extension_init(
  sqlite3 *db,
  char **pzErrMsg,
  const sqlite3_api_routines *pApi
){
    SQLITE_EXTENSION_INIT2(pApi);
 
    int rc = init_vfs(db, pzErrMsg);

    if( rc==SQLITE_OK ) rc = SQLITE_OK_LOAD_PERMANENTLY;
    return rc;
}
