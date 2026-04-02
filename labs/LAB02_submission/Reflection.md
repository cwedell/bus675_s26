# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below

First, the API URL given to the preprocessor couldn't be localhost or host.docker.internal anymore - it would have to work on the actual internet, using an actual web address. So, the inference container would have to be public-facing, at least before password or VPN protection - we wouldn't want anybody uploading random pictures to it. The shared volumes might have to live on a server hosted by one or the other datacenter, itself requiring a web address to access, or they could exist in a cloud platform. New challenges might include latency of internet connections, packet loss, or handling a service interruption in one or the other container.