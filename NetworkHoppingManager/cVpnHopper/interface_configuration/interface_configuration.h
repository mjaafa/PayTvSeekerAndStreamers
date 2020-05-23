#ifndef INTERFACE_CONFIGURATION_H
# define INTERFACE_CONFIGURATION_H
/* @brief
 *
 * Copyright (c)  2016 AZZAHRA Consulting France
 * The computer program contained herein contains proprietary
 * information which is the property of AZZAHRA Consulting France.
 * The program may be used and/or copied only with the written
 * permission of AZZAHRA Consulting France or in accordance with the
 * terms and conditions stipulated in the agreement/contract under
 * which the programs have been supplied.
 *
 * @author Mohamed Jaafar <mohamet.jaafar@gmail.com>
 */


# ifdef __cplusplus
extern "C" {
# endif
#include "cvpnhopper_types.h"
#include <sys/socket.h>
#include <netpacket/packet.h>
#include <sys/ioctl.h>
#include <linux/if_ether.h>
#include <net/if.h>

/**
 *
 * \brief       gets the interface to configure and make network traffic on it.
 *
 * \param[in]   char[IFNAMSIZ]    interface_name  : interface name  .
 * \param[in]   int               sockfd          : socket file desc.
 * \return int  socket fd.
 * \author      mohamed.jaafar.vp\@protonmail.ch
 * \date        2020
 */
int ifconf_get_interface_configuration(int socket, char interface_name[IFNAMSIZ]);

/**
 *
 * \brief       gets hardware mac address.
 *
 * \param[in]   char[IFNAMSIZ]    interface_name  : interface name.
 * \return char mac address.
 * \author      mohamed.jaafar.vp\@protonmail.ch
 * \date        2020
 */
unsigned char* ifconf_get_hardware_mac_address(char interface_name[IFNAMSIZ]);

# ifdef __cplusplus
}
# endif

#endif /* !INTERFACE_CONFIGURATION_H */
