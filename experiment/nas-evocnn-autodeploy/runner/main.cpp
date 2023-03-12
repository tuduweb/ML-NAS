#include <iostream>
#include <net.h>

void pretty_print(const ncnn::Mat& m)
{
	for (int q = 0; q < m.c; q++)
	{
		const float* ptr = m.channel(q);
		for (int y = 0; y < m.h; y++)
		{
			for (int x = 0; x < m.w; x++)
			{
				printf("%f ", ptr[x]);
			}
			ptr += m.w;
			printf("\n");
		}
		printf("------------------------\n");
	}
}

int main(int argc, char* argv[]) {
	ncnn::Net* net = new ncnn::Net();
	net->opt.use_vulkan_compute = false;
	net->opt.use_fp16_arithmetic = true;
	//net->load_param("D:/github/ncnn-resources/model.pnnx.param");
	//net->load_model("D:/github/ncnn-resources/model.pnnx.bin");

    if(argc == 1) {
        printf("argc == 1");
    }else if(argc == 2) {

        
        /* 读取模型 */
        std::string path = "/home/n504/onebinary/lightweight/ML-CL-DDoS/project/nas/experiments/indi/indi00031_00028.ncnn";
        //std::string path(argv[1]);

        std::string paramPath = path + ".param";
        std::string modelPath = path + ".bin";

        net->load_param(paramPath.c_str());
        net->load_model(modelPath.c_str());

        auto ex = net->create_extractor();
        // 另外，ncnn::Extractor还可以设置一个轻模式省内存 即set_light_mode(true)，原理是net中每个layer都会产生blob，除了最后的结果和多分支中间结果，大部分blob都不值得保留，开启轻模式可以在运算后自动回收，省下内存。但需要注意的是，一旦开启这个模式，我们就不能获得中间层的特征值了，因为中间层的内存在获得最终结果之前都被回收掉了。例如：某网络结构为 A -> B -> C，在轻模式下，向ncnn索要C结果时，A结果会在运算B时自动回收，而B结果会在运算C时自动回收，最后只保留C结果，后面再需要C结果会直接获得，满足大多数深度网络的使用方式。
        ex.set_light_mode(false);
        ex.set_num_threads(1);

        /* 读取测试数据 */
        ncnn::Mat input;

        // float inputData[63] = { 0.4963f, 0.7682f, 0.0885, 0.1320, 0.3074, 0.6341, 0.4901, 0.8964, 0.4556,
        // 	0.6323, 0.3489, 0.4017, 0.0223, 0.1689, 0.2939, 0.5185, 0.6977, 0.8000,
        // 	0.1610, 0.2823, 0.6816, 0.9152, 0.3971, 0.8742, 0.4194, 0.5529, 0.9527,
        // 	0.0362, 0.1852, 0.3734, 0.3051, 0.9320, 0.1759, 0.2698, 0.1507, 0.0317,
        // 	0.2081, 0.9298, 0.7231, 0.7423, 0.5263, 0.2437, 0.5846, 0.0332, 0.1387,
        // 	0.2422, 0.8155, 0.7932, 0.2783, 0.4820, 0.8198, 0.9971, 0.6984, 0.5675,
        // 	0.8352, 0.2056, 0.5932, 0.1123, 0.1535, 0.2417, 0.7262, 0.7011, 0.2038 };

        unsigned char coveredData[32 * 32] = { 0 };

        for (int i = 0; i < 32 * 32; ++i) {
            coveredData[i] = i;
        }

        input = ncnn::Mat::from_pixels(coveredData,ncnn::Mat::PIXEL_GRAY,32,32);

        //pretty_print(input);


        ex.input("in0", input);


        ncnn::Mat out;
        //ex.extract("F.log_softmax_0", out);
        ex.extract("out0", out);


        pretty_print(out);


    }

	return 0;
}