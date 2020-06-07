/****************************************************************************
 *  Copyright (C) 2019 RoboMaster.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of 
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program. If not, see <http://www.gnu.org/licenses/>.
 ***************************************************************************/
#include "chassis.h"

class Chassis{
public:
    ros::NodeHandle n;
    ros::Subscriber sub_chassis;
    ros::Publisher imu_pub_;
    ros::Publisher odom_pub_;
    nav_msgs::Odometry odom_;
    //! ros chassis odometry tf
    geometry_msgs::TransformStamped odom_tf_;
    //! ros chassis odometry tf broadcaster
    tf::TransformBroadcaster tf_broadcaster_;
    void execute();
    void Callback(const nav_msgs::Odometry &chassis_info);
    Chassis(){
        //ros subscriber
        sub_chassis = n.subscribe("chassis_topic",1,&Chassis::Callback,this);
        //ros publisher
        odom_pub_ = n.advertise<nav_msgs::Odometry>("/odom",30);
        std::cout << "chassis_init" <<std::endl;
        odom_.header.frame_id = "odom";
        odom_.child_frame_id = "base_link";

        odom_tf_.header.frame_id = "odom";
        odom_tf_.child_frame_id = "base_link";
    }
};

void Chassis::Callback(const nav_msgs::Odometry &chassis_info){
    std::cout << "recieve" <<std::endl;
    ros::Time current_time = ros::Time::now();
    odom_.header.stamp = current_time;
    odom_.pose.pose.position.x = chassis_info.pose.pose.position.x;
    odom_.pose.pose.position.y = chassis_info.pose.pose.position.y;
    odom_.pose.pose.position.z = 0.0;
    odom_.pose.pose.orientation = chassis_info.pose.pose.orientation;
    odom_.twist.twist.linear.x = chassis_info.twist.twist.linear.x;
    odom_.twist.twist.linear.y = chassis_info.twist.twist.linear.y;
    odom_.twist.twist.angular.z = chassis_info.twist.twist.angular.z;
    odom_pub_.publish(odom_);
    odom_tf_.header.stamp = current_time;
    odom_tf_.transform.translation.x = chassis_info.pose.pose.position.x;
    odom_tf_.transform.translation.y = chassis_info.pose.pose.position.y;

    odom_tf_.transform.translation.z = 0.0;
    odom_tf_.transform.rotation = chassis_info.pose.pose.orientation;
    tf_broadcaster_.sendTransform(odom_tf_);

}

void Chassis::execute()
{
    ros::spin();
}


int main(int argc, char **argv){
    ros::init(argc,argv,"odom");
    Chassis chassis;
    chassis.execute();
    return 0;

}

