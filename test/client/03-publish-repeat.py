#!/usr/bin/env python3

#

from mosq_test_helper import *

def do_test(proto_ver):
    rc = 1

    port = mosq_test.get_port()

    if proto_ver == 5:
        V = 'mqttv5'
    elif proto_ver == 4:
        V = 'mqttv311'
    else:
        V = 'mqttv31'

    env = {
            'LD_LIBRARY_PATH':'../../lib',
            'XDG_CONFIG_HOME':'/tmp/missing'
            }
    cmd = ['../../client/mosquitto_pub',
            '-p', str(port),
            '-q', '1',
            '-t', '03/pub/repeat/test',
            '-m', 'message',
            '-V', V,
            '--repeat', '2',
            '--repeat-delay', '0.1',
            ]

    mid = 1
    publish_packet = mosq_test.gen_publish("03/pub/repeat/test", qos=0, mid=mid, payload="message", proto_ver=proto_ver)

    broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port)

    try:
        sock = mosq_test.sub_helper(port=port, topic="#", qos=0, proto_ver=proto_ver)

        pub = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        pub.wait()

        mosq_test.expect_packet(sock, "publish 1", publish_packet)
        mosq_test.expect_packet(sock, "publish 2", publish_packet)
        rc = 0
        sock.close()
    except mosq_test.TestError:
        pass
    except Exception as e:
        print(e)
    finally:
        broker.terminate()
        broker.wait()
        (stdo, stde) = broker.communicate()
        if rc:
            print(stde.decode('utf-8'))
            print("proto_ver=%d" % (proto_ver))
            exit(rc)


do_test(proto_ver=3)
do_test(proto_ver=4)
do_test(proto_ver=5)