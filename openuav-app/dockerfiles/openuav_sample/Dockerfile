FROM nvidia/cuda:8.0-cudnn6-devel-ubuntu16.04

MAINTAINER Jnaneshwar Das <jnaneshwar.das@gmail.com> / Matt Schmittle <schmttle@udel.edu> / Abhijeet Singh <>

RUN apt-get update && apt-get install -y apt-utils \
        git

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        geographiclib-tools \
        libcurl3-dev \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python-dev \
        rsync \
        software-properties-common \
        unzip \
        zip \
        zlib1g-dev \
        openjdk-8-jdk \
        openjdk-8-jre-headless \
        python-pip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN mkdir ros-setups
COPY ros-setups ros-setups/
RUN ros-setups/ubuntu-16/setup-ros.sh 
RUN ros-setups/ubuntu-16/setup-mavlink-mavros.sh 
RUN ros-setups/ubuntu-16/setup-install.sh 
RUN ros-setups/ubuntu-16/setup-gym-gzweb-uavnav.sh
#RUN git clone https://github.com/schmittlema/ros-setups.git && cd ros-setups/ubuntu-16 && ./setup-ros.sh && ./setup-mavlink-mavros.sh && ./setup-install.sh && ./setup-gym-gzweb-uavnav.sh

RUN pip --no-cache-dir install \
         --upgrade pip \
         --upgrade virtualenv

RUN pip --no-cache-dir install \
        ipykernel \
        jupyter \
        matplotlib \
        numpy \
        scipy \
        sklearn \
        pandas \
        && \
    python -m ipykernel.kernelspec

#Don't need Jupyter
# Set up our notebook config.
#COPY jupyter_notebook_config.py /root/.jupyter/

# Jupyter has issues with being run directly:
#   https://github.com/ipython/ipython/issues/7062
# We just add a little wrapper script.
#COPY run_jupyter.sh /

# Set up Bazel.

# Running bazel inside a `docker build` command causes trouble, cf:
#   https://github.com/bazelbuild/bazel/issues/134
# The easiest solution is to set up a bazelrc file forcing --batch.
RUN echo "startup --batch" >>/etc/bazel.bazelrc
# Similarly, we need to workaround sandboxing issues:
#   https://github.com/bazelbuild/bazel/issues/418
RUN echo "build --spawn_strategy=standalone --genrule_strategy=standalone" \
    >>/etc/bazel.bazelrc
# Install the most recent bazel release.
ENV BAZEL_VERSION 0.5.0
WORKDIR /
RUN mkdir /bazel && \
    cd /bazel && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -O https://github.com/bazelbuild/bazel/releases/download/$BAZEL_VERSION/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    curl -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36" -fSsL -o /bazel/LICENSE.txt https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE && \
    chmod +x bazel-*.sh && \
    ./bazel-$BAZEL_VERSION-installer-linux-x86_64.sh && \
    cd / && \
    rm -f /bazel/bazel-$BAZEL_VERSION-installer-linux-x86_64.sh

# Download and build TensorFlow.

RUN git clone https://github.com/tensorflow/tensorflow.git && \
    cd tensorflow && \
    git checkout r1.2
WORKDIR /tensorflow

# For Nivida
LABEL com.nvidia.volumes.needed="nvidia_driver"
ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64

# Configure the build for our CUDA configuration.
ENV CI_BUILD_PYTHON python
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH
ENV TF_NEED_CUDA 1
ENV TF_CUDA_COMPUTE_CAPABILITIES=3.0,3.5,5.2,6.0,6.1

RUN pip install wheel
RUN tensorflow/tools/ci_build/builds/configured GPU \
    bazel build -c opt --config=cuda --cxxopt="-D_GLIBCXX_USE_CXX11_ABI=0" \
        tensorflow/tools/pip_package:build_pip_package
RUN bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/pip
RUN pip --no-cache-dir install --upgrade /tmp/pip/tensorflow-*.whl
RUN rm -rf /tmp/pip && \
    rm -rf /root/.cache
# Clean up pip wheel and Bazel cache when done.

RUN cd ~/src/Firmware && \
    git remote add openuav-master https://github.com/Open-UAV/Firmware && \
    git pull openuav-master master

RUN echo "source /opt/ros/kinetic/setup.bash" >> ~/.profile && \
    echo "source /opt/ros/kinetic/setup.bash" >> ~/.profile && \
    echo "source ~/catkin_ws/devel/setup.bash" >> ~/.profile && \
    echo "export GAZEBO_PLUGIN_PATH=:/root/src/Firmware/Tools/sitl_gazebo/Build" >> ~/.profile && \
    echo "export GAZEBO_MODEL_PATH=:/root/src/Firmware/Tools/sitl_gazebo/models" >> ~/.profile && \
    echo "export GAZEBO_RESOURCE_PATH=:/root/src/Firmware/Tools/sitl_gazebo/media" >> ~/.profile && \
    echo "export PYTHONPATH=/root/catkin_ws/devel/lib/python2.7/dist-packages:/opt/ros/jade/lib/python2.7/dist-packages" >> ~/.profile

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-kinetic-web-video-server \
        ros-kinetic-image-geometry
RUN apt-get install -y ros-kinetic-rosbridge-server ros-kinetic-opencv-apps

RUN cd ~/catkin_ws && \
    catkin build

ADD install_geographiclib_datasets.sh /home/
RUN cd /home && \
    chmod +x install_geographiclib_datasets.sh && \
    ./install_geographiclib_datasets.sh

RUN sed -i '/force_color_prompt/s/^#//g' ~/.bashrc

### Django set up to expose various states from the simulation container
RUN apt-get -y install python3-pip
RUN pip3 --no-cache-dir install Django
RUN mkdir /django 
RUN django-admin startproject DjangoProject /django
RUN python3 /django/manage.py startapp query
COPY django_files/project_urls.py /django/DjangoProject/urls.py
COPY django_files/query_urls.py /django/query/urls.py
COPY django_files/query_view.py /django/query/views.py
RUN sed -i '/ALLOWED_HOSTS/c\ALLOWED_HOSTS = ['\''*'\'']' /django/DjangoProject/settings.py
### Django set up to expose various states from the simulation container

# Wetty - web tty
RUN mkdir /wetty
RUN npm explore npm -g -- npm install node-gyp@latest
RUN cd /wetty && git clone https://github.com/krishnasrinivas/wetty && \
    cd wetty && npm install

# Adding user term and giving permissions
RUN useradd -d /simulation -m -s /bin/bash term
RUN echo 'term:term' | chpasswd
RUN chmod -R 777 /root/src
RUN chmod -R 777 /simulation
RUN chmod -R 777 /opt/ros
RUN find /root -type d -exec chmod 755 {} \;

# Ensure the setup.sh is in the last, so that we can build again quickly if setup changes
ADD setup.sh /home/
RUN chmod +x /home/setup.sh

WORKDIR /root

RUN ["/bin/bash"]
