#ifndef CVPNHOPPER_TYPES_H
# define CVPNHOPPER_TYPES_H
/* @brief
 *
 * Copyright (c) 2020
 *
 * The computer program contained herein contains proprietary
 * information which is the property of Mohamed JAAFAR.
 * The program may be used and/or copied only with the written 
 * permission of Mohamed JAAFAR or in accordance with the
 * terms and conditions stipulated in the agreement/contract under
 * which the programs have been supplied.
 *
 * @author Mohamed Jaafar <mohamet.jaafar.vp@protonmail.ch>
 */

/**
* @defgroup CVPNHOPPER CVPNHOPPER
* \{ */
/**
* @defgroup CVPNHOPPER_TYPES_H CVPNHOPPER_TYPES_H
* \{ */ 


# ifdef __cplusplus
extern "C" {
# endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/* ##########################################################################################
** #                                        MACROS                                          #
** ##########################################################################################*/
/**
** @brief defines macro for more secured asprintf.
*/
#define Sasprintf(write_to, ...) {\
char *tmp_string_for_extend = write_to; \
    asprintf(&(write_to), __VA_ARGS__); \
free(tmp_string_for_extend); \
}

/**
** @brief defines macro for unused variables.
*/
#define UNUSED_VARIABLE(x) (x=x)

/**
** @brief defines macro for unused pointers.
*/
#define UNUSED_POINTER(p)  (*p)

/**
** @brief defines macro for private functions.
*/
//#define PRIVATE             static


/**
** @brief defines macro for private debug system using module restrictions.
*/

#define CVPNHOPPER_ERROR( ...)          \
    printf("\033[31m"); printf("[%s]%s : %d > ",MODULE,__FUNCTION__,__LINE__);\
    printf( __VA_ARGS__);printf("\033[0m \n")
#define CVPNHOPPER_WARNING( ...)        \
    printf("\033[33m"); printf("[%s]%s : %d > ",MODULE,__FUNCTION__,__LINE__);\
    printf( __VA_ARGS__);printf("\033[0m \n")
#define CVPNHOPPER_INFO( ...)           \
    printf("\033[32m"); printf("[%s]%s : %d > ",MODULE,__FUNCTION__,__LINE__);\
    printf( __VA_ARGS__);printf("\033[0m \n")
#define CVPNHOPPER_LOG( ...)            \
    printf("\033[34m"); printf("[%s]%s : %d > ",MODULE,__FUNCTION__,__LINE__);\
    printf( __VA_ARGS__);printf("\033[0m \n")
#define CVPNHOPPER_DEBUG( ...)         \
    printf("\033[36m"); printf("[%s]%s : %d > ",MODULE,__FUNCTION__,__LINE__);\
    printf( __VA_ARGS__);printf("\033[0m \n")

/* ##########################################################################################
** #                                       TYPEDEFS                                         #
** ##########################################################################################*/

/**
** @brief enumerates the error types in SAMPLE module.
*/
typedef enum CVPNHOPPER_Error_e
{
    CVPNHOPPER_RET_OK                        ,       /*!< no error                               */
    CVPNHOPPER_RET_ERROR                     ,       /*!< specific dbus error                    */
    CVPNHOPPER_RET_MAX

}CVPNHOPPER_Error_t;

/**
** \brief defines the mac address size
*/
#define IFMACSIZ    6

/**
** \brief defines function name as COMMAND stringify.
*/
#define CAPA_NAME(NAME)    #NAME
//#define COMMAND(NAME)  { #NAME, NAME ## _command }
/*struct command
{
  char *name;
  void (*function) ();
};*/
# ifdef __cplusplus
}
# endif
// CVPNHOPPER_TYPES
/** \} */
// CVPNHOPPER
/** \} */
#endif /* !CVPNHOPPER_TYPES_H */
