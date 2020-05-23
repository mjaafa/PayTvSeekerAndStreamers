/* @brief
 *
 * Copyright (c) 2020 
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
* @defgroup CVPNHOPPER CVPNHOPPER
* \{ */
/**
* @defgroup INTERFACE_CONFIGURATION INTERFACE_CONFIGURATION
* \{ */
/* ##########################################################################################
** #                                       DEFINES                                          #
** ##########################################################################################*/
#define MODULE      "INTERFACE_CONFIGURATION"

/* ##########################################################################################
** #                                       INCLUDES                                         #
** ##########################################################################################*/
#include "cvpnhopper_types.h"
#include "interface_configuration.h"
/**
 *
 * \brief       gets the interface to configure and make network traffic on it.
 *
 * \param[in]   char[IFNAMSIZ]    interface_name  : interface name  .
 * \param[in]   int               sockfd          : socket file desc.
 * \return int  interface index.
 * \author      mohamed.jaafar.vp\@protonmail.ch
 * \date        2020
 */
/* Get the index of the interface to send on */
int get_interface_index(char interface_name[IFNAMSIZ], int sockfd)
{
    struct ifreq if_idx;
    memset(&if_idx, 0, sizeof(struct ifreq));
    strncpy(if_idx.ifr_name, interface_name, IFNAMSIZ-1);
    if (ioctl(sockfd, SIOCGIFINDEX, &if_idx) < 0)
            CVPNHOPPER_ERROR("SIOCGIFINDEX");

    return if_idx.ifr_ifindex;
}

unsigned char* ifconf_get_hardware_mac_address(char interface_name[IFNAMSIZ])
{
    int fd;
    struct ifreq ifr;
    unsigned char mac[IFMACSIZ];
    int i;

    memset(mac, 0, (sizeof(unsigned char) * IFMACSIZ));

    CVPNHOPPER_INFO(" get mac address for ifname %s ", interface_name);

    fd = socket(AF_INET, SOCK_DGRAM, 0);

    ifr.ifr_addr.sa_family = AF_INET;
    strncpy(ifr.ifr_name , &interface_name[0] , IFNAMSIZ-1);

    ioctl(fd, SIOCGIFHWADDR, &ifr);

    close(fd);

    for (i=0; i<(IFMACSIZ/2); i++)
    {
        sprintf(&mac[i*2],"%02X",((unsigned char*)ifr.ifr_hwaddr.sa_data)[i]);
    }

    mac[IFMACSIZ]='\0';
    CVPNHOPPER_INFO(" get mac address for ifname %s : %s", interface_name, mac);
 
    return strdup(mac);
}

void ifconf_get_interface_configuration(char interface_name[IFNAMSIZ])
{
    int sockfd;
    struct sockaddr_ll socket_address;
    socket_address.sll_ifindex = get_interface_index(interface_name, sockfd);
    /* Address length*/
    socket_address.sll_halen = ETH_ALEN;

    /* Destination MAC */
    memcpy(socket_address.sll_addr, get_hardware_mac_address(interface_name), ETH_ALEN);
}
