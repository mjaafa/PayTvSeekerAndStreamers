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

int main (void)
{
    int z_ret = CVPNHOPPER_RET_OK;
    unsigned char mac_address[IFMACSIZ];
    char *if_name = "wlp59s0";
//    CVPNHOPPER_INFO(" mac address ifname wlp59s0 : %s",  ifconf_get_hardware_mac_address(if_name));

    memcpy(&mac_address,strdup(ifconf_get_hardware_mac_address(if_name)), IFMACSIZ);
    CVPNHOPPER_INFO(" mac address ifname wlp59s0 : %s",  mac_address);

    return z_ret;
}
