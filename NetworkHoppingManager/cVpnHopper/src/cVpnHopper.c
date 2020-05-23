/* @brief
 *
 * Copyright (c)  2020
 * The computer program contained herein contains proprietary
 * information which is the property of Mohamed JAAFAR.
 * The program may be used and/or copied only with the written
 * permission Mohamed JAAFAR or in accordance with the
 * terms and conditions stipulated in the agreement/contract under
 * which the programs have been supplied.
 *
 * @author Mohamed Jaafar <mohamed.jaafar.vp@protonmail.ch>
 */

/**
* @defgroup CVPNHOPPING CVPNHOPPING
* \{ */
/**
* @defgroup COMMON COMMON
* \{ */
/* ##########################################################################################
** #                                       INCLUDES                                         #
** ##########################################################################################*/
#define MODULE "COMMON"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


// if you have no good reason to use void*, use the type
// you've allocated. while it usually works for built-in
// types, it wouldn't work for classes (it wouldn't call
// the destructor)
#include "cvpnhopper_types.h"
#include "cVpnHopper.h"
#ifdef INTERFACE_CONFIGURATION
#include "interface_configuration.h"
#endif /* !INTERFACE_CONFIGURATION */

/* ##########################################################################################
** #                                   DEFINES & MACROS                                     #
** ##########################################################################################*/

/* ##########################################################################################
** #                                       TYPEDEFS                                         #
** ##########################################################################################*/
/* ##########################################################################################
** #                                       FUNCTIONS                                        #
** ##########################################################################################*/

/*##############################################################################*/
/*
*
*/

char* get_capabilities(void)
{
//    char capabilities_supported [] = CAPA_NAME(get_hardware_mac_addres;;
//                                     CAPA_NAME(get_interface_configuration) ;
    return "get_interface_configuration";
}

unsigned char* get_hardware_mac_address(char interface_name[IFNAMSIZ])
{
    return ifconf_get_hardware_mac_address(&interface_name[0]);
}

int get_interface_configuration (int socket, char interface_name[IFNAMSIZ])
{
    return ifconf_get_interface_configuration(socket, &interface_name[0]);
}
